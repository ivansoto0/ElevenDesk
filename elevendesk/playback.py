import gc
import os
import struct
import tempfile
import threading
import time
import wave

import soundobj

from elevendesk import constants


_playback_lock = threading.RLock()
_current_sound = None
_current_temp_path = None


def _close_sound(sound):
	if sound is None:
		return
	if getattr(sound, constants.SOUNDOBJ_ATTR_LOADED, False):
		soundobj.lib.ma_sound_uninit(sound._sound)
		sound._loaded = False


def _remove_temp_file(file_path):
	if not file_path:
		return
	try:
		os.remove(file_path)
	except FileNotFoundError:
		pass


def stop_audio():
	global _current_sound
	global _current_temp_path
	with _playback_lock:
		sound = _current_sound
		temp_path = _current_temp_path
		_current_sound = None
		_current_temp_path = None
		if sound is not None:
			sound.stop()
			_close_sound(sound)
		_remove_temp_file(temp_path)


def _ulaw_sample_to_pcm(sample):
	inverted_sample = ~sample & constants.ULAW_BYTE_MASK
	sign = inverted_sample & constants.ULAW_SIGN_BIT
	exponent = (inverted_sample >> constants.ULAW_EXPONENT_SHIFT) & constants.ULAW_EXPONENT_MASK
	mantissa = inverted_sample & constants.ULAW_MANTISSA_MASK
	pcm_sample = ((mantissa << constants.ULAW_MANTISSA_SHIFT) + constants.ULAW_BIAS) << exponent
	pcm_sample -= constants.ULAW_BIAS
	if sign:
		pcm_sample = -pcm_sample
	return pcm_sample


def _convert_ulaw_to_pcm(audio_bytes):
	return b"".join(
		struct.pack(constants.PCM_SAMPLE_PACK_FORMAT, _ulaw_sample_to_pcm(sample))
		for sample in audio_bytes
	)


def _write_wave_file(file_path, audio_bytes, sample_rate):
	with wave.open(file_path, constants.FILE_MODE_BINARY_WRITE) as wave_file:
		wave_file.setnchannels(constants.MONO_CHANNEL_COUNT)
		wave_file.setsampwidth(constants.AUDIO_SAMPLE_WIDTH)
		wave_file.setframerate(sample_rate)
		wave_file.writeframes(audio_bytes)


def _create_temp_audio_file(audio_bytes, output_format):
	if output_format.startswith(constants.OUTPUT_MP3_PREFIX):
		file_suffix = constants.EXTENSION_MP3
	elif output_format in (constants.OUTPUT_PCM_44100, constants.OUTPUT_ULAW_8000):
		file_suffix = constants.EXTENSION_WAV
	else:
		raise ValueError(constants.ERROR_UNSUPPORTED_AUDIO)
	file_descriptor, file_path = tempfile.mkstemp(
		prefix=constants.TEMP_AUDIO_PREFIX,
		suffix=file_suffix,
	)
	os.close(file_descriptor)
	try:
		if output_format.startswith(constants.OUTPUT_MP3_PREFIX):
			with open(file_path, constants.FILE_MODE_BINARY_WRITE) as audio_file:
				audio_file.write(audio_bytes)
		elif output_format == constants.OUTPUT_PCM_44100:
			_write_wave_file(file_path, audio_bytes, constants.PCM_SAMPLE_RATE)
		else:
			_write_wave_file(
				file_path,
				_convert_ulaw_to_pcm(audio_bytes),
				constants.ULAW_SAMPLE_RATE,
			)
	except (OSError, ValueError, wave.Error):
		_remove_temp_file(file_path)
		raise
	return file_path


def get_audio_file_metadata(file_path):
	sound = soundobj.Sound(source=file_path)
	try:
		audio_format = soundobj.ffi.new(constants.SOUNDOBJ_FORMAT_POINTER)
		channel_count = soundobj.ffi.new(constants.SOUNDOBJ_UINT_POINTER)
		sample_rate = soundobj.ffi.new(constants.SOUNDOBJ_UINT_POINTER)
		result = soundobj.lib.ma_sound_get_data_format(
			sound._sound,
			audio_format,
			channel_count,
			sample_rate,
			soundobj.ffi.NULL,
			constants.SOUNDOBJ_CHANNEL_MAP_CAPACITY,
		)
		if result != soundobj.lib.MA_SUCCESS:
			raise soundobj.MiniAudioError(constants.ERROR_AUDIO_METADATA)
		return {
			constants.KEY_FILE_PATH: file_path,
			constants.KEY_FILE_NAME: os.path.basename(file_path),
			constants.KEY_FILE_DURATION: sound.length_in_seconds,
			constants.KEY_FILE_FORMAT: os.path.splitext(file_path)[constants.INDEX_STEP].lstrip(constants.DOT).upper(),
			constants.KEY_FILE_SAMPLE_RATE: sample_rate[constants.FIRST_ITEM_INDEX],
			constants.KEY_FILE_CHANNELS: channel_count[constants.FIRST_ITEM_INDEX],
			constants.KEY_FILE_SIZE: os.path.getsize(file_path),
		}
	finally:
		_close_sound(sound)


def play_audio(audio_bytes, output_format):
	def playback_worker():
		global _current_sound
		global _current_temp_path
		temp_path = _create_temp_audio_file(audio_bytes, output_format)
		sound = soundobj.Sound(source=temp_path)
		with _playback_lock:
			stop_audio()
			_current_sound = sound
			_current_temp_path = temp_path
			sound.play()
		while sound.is_playing:
			time.sleep(constants.PLAYBACK_POLL_SECONDS)
		with _playback_lock:
			if _current_sound is sound:
				_current_sound = None
				_current_temp_path = None
				_close_sound(sound)
				gc.collect()
				_remove_temp_file(temp_path)

	playback_thread = threading.Thread(target=playback_worker, daemon=constants.THREAD_DAEMON)
	playback_thread.start()
	return playback_thread
