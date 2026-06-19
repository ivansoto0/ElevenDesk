import audioop
import io
import os
import threading
import time

from sound_lib.output import Output
from sound_lib.main import BassError
from sound_lib.stream import FileStream
from sound_lib.stream import FileUserStream
from sound_lib.stream import PushStream

from elevendesk import constants


_playback_lock = threading.RLock()
_output = None
_current_stream = None
_current_buffer = None


def _get_output():
	global _output
	if _output is None:
		_output = Output()
	return _output


def stop_audio():
	global _current_stream
	global _current_buffer
	with _playback_lock:
		if _current_stream is not None:
			try:
				_current_stream.stop()
				_current_stream.free()
			except (BassError, RuntimeError, OSError):
				pass
		_current_stream = None
		_current_buffer = None


def _create_stream(audio_bytes, output_format):
	global _current_buffer
	if output_format.startswith(constants.OUTPUT_MP3_PREFIX):
		_current_buffer = io.BytesIO(audio_bytes)
		return FileUserStream(_current_buffer)
	if output_format == constants.OUTPUT_PCM_44100:
		stream = PushStream(freq=constants.PCM_SAMPLE_RATE, chans=constants.MONO_CHANNEL_COUNT)
		stream.push(audio_bytes)
		stream.push_end()
		return stream
	if output_format == constants.OUTPUT_ULAW_8000:
		pcm_bytes = audioop.ulaw2lin(audio_bytes, constants.AUDIO_SAMPLE_WIDTH)
		stream = PushStream(freq=constants.ULAW_SAMPLE_RATE, chans=constants.MONO_CHANNEL_COUNT)
		stream.push(pcm_bytes)
		stream.push_end()
		return stream
	raise ValueError(constants.ERROR_UNSUPPORTED_AUDIO)


def get_audio_file_metadata(file_path):
	_get_output()
	stream = FileStream(file=file_path)
	try:
		channel_info = stream.get_info()
		return {
			constants.KEY_FILE_PATH: file_path,
			constants.KEY_FILE_NAME: os.path.basename(file_path),
			constants.KEY_FILE_DURATION: stream.length_in_seconds(),
			constants.KEY_FILE_FORMAT: os.path.splitext(file_path)[constants.INDEX_STEP].lstrip(constants.DOT).upper(),
			constants.KEY_FILE_SAMPLE_RATE: channel_info.freq,
			constants.KEY_FILE_CHANNELS: channel_info.chans,
			constants.KEY_FILE_SIZE: os.path.getsize(file_path),
		}
	finally:
		stream.free()


def play_audio(audio_bytes, output_format):
	def playback_worker():
		global _current_stream
		with _playback_lock:
			stop_audio()
			_get_output()
			_current_stream = _create_stream(audio_bytes, output_format)
			_current_stream.play()
		while _current_stream is not None and _current_stream.is_playing:
			time.sleep(constants.PLAYBACK_POLL_SECONDS)

	playback_thread = threading.Thread(target=playback_worker, daemon=constants.THREAD_DAEMON)
	playback_thread.start()
	return playback_thread
