import atexit
import io
import os
import platform
import struct
import tempfile
import threading
import time
import wave

from sound_lib.input import Input
from sound_lib.main import BassError
from sound_lib.output import Output
from sound_lib.stream import FileStream

from elevendesk import config
from elevendesk import constants


_lock = threading.RLock()
_output = None
_current_stream = None


def _resolve_output_device():
	saved = config.load_config()[constants.KEY_OUTPUT_DEVICE]
	if not saved:
		return -1
	try:
		names = Output.get_device_names()
		return names.index(saved) + 1
	except (ValueError, Exception):
		return -1


def _get_output():
	global _output
	with _lock:
		if _output is None:
			_output = Output(device=_resolve_output_device())
	return _output


def reset_output():
	global _output
	stop_audio()
	with _lock:
		if _output is not None:
			try:
				_output.free()
			except Exception:
				pass
			_output = None


def stop_audio():
	global _current_stream
	with _lock:
		stream = _current_stream
		_current_stream = None
	if stream is not None:
		try:
			stream.stop()
			stream.free()
		except Exception:
			pass


def _ulaw_sample_to_pcm(sample):
	inverted = ~sample & constants.ULAW_BYTE_MASK
	sign = inverted & constants.ULAW_SIGN_BIT
	exponent = (inverted >> constants.ULAW_EXPONENT_SHIFT) & constants.ULAW_EXPONENT_MASK
	mantissa = inverted & constants.ULAW_MANTISSA_MASK
	pcm = ((mantissa << constants.ULAW_MANTISSA_SHIFT) + constants.ULAW_BIAS) << exponent
	pcm -= constants.ULAW_BIAS
	if sign:
		pcm = -pcm
	return pcm


def _convert_ulaw_to_pcm(audio_bytes):
	return b''.join(
		struct.pack(constants.PCM_SAMPLE_PACK_FORMAT, _ulaw_sample_to_pcm(sample))
		for sample in audio_bytes
	)


def _to_wav_bytes(audio_bytes, sample_rate):
	buf = io.BytesIO()
	with wave.open(buf, 'wb') as wf:
		wf.setnchannels(constants.MONO_CHANNEL_COUNT)
		wf.setsampwidth(constants.AUDIO_SAMPLE_WIDTH)
		wf.setframerate(sample_rate)
		wf.writeframes(audio_bytes)
	return buf.getvalue()


def _prepare_audio(audio_bytes, output_format):
	if output_format.startswith(constants.OUTPUT_MP3_PREFIX):
		return audio_bytes
	if output_format == constants.OUTPUT_PCM_44100:
		return _to_wav_bytes(audio_bytes, constants.PCM_SAMPLE_RATE)
	if output_format == constants.OUTPUT_ULAW_8000:
		return _to_wav_bytes(_convert_ulaw_to_pcm(audio_bytes), constants.ULAW_SAMPLE_RATE)
	raise ValueError(constants.ERROR_UNSUPPORTED_AUDIO)


def _create_stream(data, output_format):
	# sound_lib FileStream(mem=True) crashes on macOS: it unconditionally calls
	# file.encode() on the bytes argument, treating it as a path string.
	# Write to a temp file instead and return the path for later cleanup.
	if platform.system() == "Darwin":
		suffix = constants.EXTENSION_MP3 if output_format.startswith(constants.OUTPUT_MP3_PREFIX) else constants.EXTENSION_WAV
		fd, tmp_path = tempfile.mkstemp(suffix=suffix)
		try:
			os.write(fd, data)
		finally:
			os.close(fd)
		return FileStream(file=tmp_path), tmp_path
	return FileStream(mem=True, file=data, length=len(data)), None


def play_audio(audio_bytes, output_format, on_finished=None):
	def worker():
		global _current_stream
		tmp_path = None
		try:
			data = _prepare_audio(audio_bytes, output_format)
			_get_output()
			stream, tmp_path = _create_stream(data, output_format)
		except Exception:
			if on_finished is not None:
				on_finished()
			return
		with _lock:
			old = _current_stream
			_current_stream = stream
		if old is not None:
			try:
				old.stop()
				old.free()
			except Exception:
				pass
		stream.play()
		try:
			while stream.is_playing or stream.is_paused:
				time.sleep(constants.PLAYBACK_POLL_SECONDS)
		except Exception:
			pass
		with _lock:
			if _current_stream is stream:
				_current_stream = None
		try:
			stream.free()
		except Exception:
			pass
		if tmp_path is not None:
			try:
				os.unlink(tmp_path)
			except OSError:
				pass
		if on_finished is not None:
			on_finished()

	thread = threading.Thread(target=worker, daemon=constants.THREAD_DAEMON)
	thread.start()
	return thread


def pause_audio():
	with _lock:
		stream = _current_stream
		if stream is None:
			return False
		try:
			if not stream.is_playing:
				return False
			stream.pause()
		except Exception:
			return False
	return True


def resume_audio():
	with _lock:
		stream = _current_stream
		if stream is None:
			return False
		try:
			if not stream.is_paused:
				return False
			stream.play()
		except Exception:
			return False
	return True


def get_audio_file_metadata(file_path):
	_get_output()
	stream = FileStream(file=file_path)
	try:
		info = stream.get_info()
		return {
			constants.KEY_FILE_PATH: file_path,
			constants.KEY_FILE_NAME: os.path.basename(file_path),
			constants.KEY_FILE_DURATION: stream.length_in_seconds(),
			constants.KEY_FILE_FORMAT: os.path.splitext(file_path)[constants.INDEX_STEP].lstrip(constants.DOT).upper(),
			constants.KEY_FILE_SAMPLE_RATE: info.freq,
			constants.KEY_FILE_CHANNELS: info.chans,
			constants.KEY_FILE_SIZE: os.path.getsize(file_path),
		}
	finally:
		stream.free()


def get_devices():
	playback = []
	capture = []
	try:
		playback = list(Output.get_device_names())
	except Exception:
		pass
	try:
		capture = list(Input.get_device_names())
	except Exception:
		pass
	return playback, capture


def cleanup():
	global _output
	stop_audio()
	with _lock:
		if _output is not None:
			try:
				_output.free()
			except Exception:
				pass
			_output = None


atexit.register(cleanup)
