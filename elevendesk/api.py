import datetime

from elevenlabs.client import ElevenLabs
from elevenlabs.core import ApiError
from elevenlabs.types import VoiceSettings
import httpx

from elevendesk import config
from elevendesk import constants


class ElevenDeskAPIError(Exception):
	pass


_client = None
_client_api_key = None


def get_client():
	global _client
	global _client_api_key
	api_key = config.load_config()[constants.KEY_API_KEY]
	if not api_key:
		raise ElevenDeskAPIError(constants.ERROR_API_KEY_REQUIRED)
	if _client is None or api_key != _client_api_key:
		try:
			_client = ElevenLabs(api_key=api_key)
		except (TypeError, ValueError) as error:
			raise ElevenDeskAPIError(str(error)) from error
		_client_api_key = api_key
	return _client


def reset_client():
	global _client
	global _client_api_key
	_client = None
	_client_api_key = None


def _get_attribute(value, attribute_name, default_value=None):
	if isinstance(value, dict):
		return value.get(attribute_name, default_value)
	return getattr(value, attribute_name, default_value)


def _get_collection(response, attribute_name):
	collection = _get_attribute(response, attribute_name, response)
	if collection is None:
		return []
	return list(collection)


def _join_audio_chunks(response):
	if isinstance(response, bytes):
		return response
	if isinstance(response, bytearray):
		return bytes(response)
	try:
		return b"".join(response)
	except ApiError as error:
		raise ElevenDeskAPIError(_format_api_error(error)) from error
	except (httpx.HTTPError, OSError, TypeError, ValueError) as error:
		raise ElevenDeskAPIError(str(error)) from error


def _format_api_error(error):
	body = error.body
	if isinstance(body, dict):
		detail = body.get(constants.API_ERROR_DETAIL, body)
		if isinstance(detail, dict):
			message = detail.get(constants.API_ERROR_MESSAGE)
			request_id = detail.get(constants.API_ERROR_REQUEST_ID)
			if message and request_id:
				return constants.ERROR_API_REQUEST_ID_TEMPLATE.format(message, request_id)
			if message:
				return message
		if isinstance(detail, str):
			return detail
	return str(error)


def _call_sdk(callable_object, keyword_arguments):
	try:
		return callable_object(**keyword_arguments)
	except (ElevenDeskAPIError, KeyboardInterrupt, SystemExit):
		raise
	except ApiError as error:
		raise ElevenDeskAPIError(_format_api_error(error)) from error
	except (httpx.HTTPError, OSError, TypeError, ValueError, AttributeError) as error:
		raise ElevenDeskAPIError(str(error)) from error


def _get_sdk_section(client, section_name):
	try:
		return getattr(client, section_name)
	except AttributeError as error:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE) from error


def _get_sdk_method(client, section_name, method_name):
	section = _get_sdk_section(client, section_name)
	try:
		return getattr(section, method_name)
	except AttributeError as error:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE) from error


def get_voices():
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICES, constants.API_ATTR_GET_ALL),
		{},
	)
	voices = []
	for voice in _get_collection(response, constants.API_ATTR_VOICES):
		voice_id = _get_attribute(voice, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT)
		voices.append({
			constants.KEY_ID: voice_id,
			constants.KEY_VOICE_ID: voice_id,
			constants.KEY_NAME: _get_attribute(voice, constants.API_ATTR_NAME, constants.EMPTY_TEXT),
			constants.KEY_CATEGORY: _get_attribute(voice, constants.API_ATTR_CATEGORY, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
			constants.KEY_DESCRIPTION: _get_attribute(voice, constants.API_ATTR_DESCRIPTION, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
		})
	return voices


def get_models():
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_MODELS, constants.API_ATTR_GET_ALL),
		{},
	)
	models = []
	for model in _get_collection(response, constants.API_ATTR_MODELS):
		models.append({
			constants.KEY_ID: _get_attribute(model, constants.API_ATTR_MODEL_ID, constants.EMPTY_TEXT),
			constants.KEY_NAME: _get_attribute(model, constants.API_ATTR_NAME, constants.EMPTY_TEXT),
		})
	return models


def text_to_speech(text, voice_id, model_id, voice_settings, output_format):
	client = get_client()
	try:
		sdk_voice_settings = VoiceSettings(**voice_settings)
	except (TypeError, ValueError) as error:
		raise ElevenDeskAPIError(str(error)) from error
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_TEXT_TO_SPEECH, constants.API_ATTR_CONVERT),
		{
			constants.API_KW_TEXT: text,
			constants.API_KW_VOICE_ID: voice_id,
			constants.API_KW_MODEL_ID: model_id,
			constants.API_KW_VOICE_SETTINGS: sdk_voice_settings,
			constants.API_KW_OUTPUT_FORMAT: output_format,
		},
	)
	return _join_audio_chunks(response)


def speech_to_text(audio_bytes, model_id):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_SPEECH_TO_TEXT, constants.API_ATTR_CONVERT),
		{
			constants.API_KW_FILE: audio_bytes,
			constants.API_KW_MODEL_ID: model_id,
		},
	)
	text = _get_attribute(response, constants.API_ATTR_TEXT, response)
	if not isinstance(text, str):
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE)
	return text


def generate_sound_effect(prompt, duration_seconds):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_SOUND_GENERATION, constants.API_ATTR_CONVERT),
		{
			constants.API_KW_TEXT: prompt,
			constants.API_KW_DURATION_SECONDS: duration_seconds,
		},
	)
	return _join_audio_chunks(response)


def design_voice(prompt, name):
	client = get_client()
	preview_response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_VOICE_DESIGN, constants.API_ATTR_CREATE_PREVIEWS),
		{
			constants.API_KW_VOICE_DESCRIPTION: prompt,
			constants.API_KW_TEXT: prompt,
		},
	)
	previews = _get_collection(preview_response, constants.API_ATTR_PREVIEWS)
	if not previews:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE)
	preview = previews[constants.FIRST_ITEM_INDEX]
	preview_id = _get_attribute(preview, constants.API_ATTR_VOICE_PREVIEW, constants.EMPTY_TEXT)
	if not preview_id:
		preview_id = _get_attribute(preview, constants.API_KW_GENERATED_VOICE_ID, constants.EMPTY_TEXT)
	create_method = _get_sdk_method(
		client,
		constants.API_ATTR_VOICE_DESIGN,
		constants.API_ATTR_VOICE_DESIGN_CREATE,
	)
	voice_response = _call_sdk(
		create_method,
		{
			constants.API_KW_GENERATED_VOICE_ID: preview_id,
			constants.API_KW_VOICE_NAME: name,
			constants.API_KW_VOICE_DESCRIPTION: prompt,
		},
	)
	return {
		constants.KEY_VOICE_ID: _get_attribute(voice_response, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT),
		constants.KEY_NAME: _get_attribute(voice_response, constants.API_ATTR_NAME, name),
	}


def clone_voice(name, description, file_paths):
	if len(file_paths) > constants.CLONE_MAX_AUDIO_FILES:
		raise ElevenDeskAPIError(
			constants.ERROR_CLONE_FILE_LIMIT_TEMPLATE.format(constants.CLONE_MAX_AUDIO_FILES)
		)
	client = get_client()
	opened_files = []
	try:
		for file_path in file_paths:
			opened_files.append(open(file_path, constants.FILE_MODE_BINARY_READ))
		voices_client = _get_sdk_section(client, constants.API_ATTR_VOICES)
		ivc_client = getattr(voices_client, constants.API_ATTR_IVC)
		response = _call_sdk(
			getattr(ivc_client, constants.API_ATTR_CREATE),
			{
				constants.API_KW_NAME: name,
				constants.API_KW_DESCRIPTION: description,
				constants.API_KW_FILES: opened_files,
			},
		)
	except (AttributeError, OSError) as error:
		raise ElevenDeskAPIError(str(error)) from error
	finally:
		for opened_file in opened_files:
			opened_file.close()
	return {
		constants.KEY_VOICE_ID: _get_attribute(response, constants.API_ATTR_VOICE_ID, constants.EMPTY_TEXT),
		constants.KEY_NAME: _get_attribute(response, constants.API_ATTR_NAME, name),
	}


def get_history():
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_HISTORY, constants.API_ATTR_GET_ALL),
		{constants.API_KW_PAGE_SIZE: constants.HISTORY_PAGE_SIZE},
	)
	history_items = []
	for item in _get_collection(response, constants.API_ATTR_HISTORY_ITEMS):
		date_value = _get_attribute(item, constants.API_ATTR_DATE, constants.EMPTY_TEXT)
		if isinstance(date_value, (int, float)):
			date_time = datetime.datetime.fromtimestamp(date_value)
			date_value = constants.HISTORY_DATE_TEMPLATE.format(
				date_time.strftime(constants.HISTORY_DATE_PREFIX_FORMAT),
				date_time.day,
				date_time.year,
			)
		history_items.append({
			constants.KEY_HISTORY_ITEM_ID: _get_attribute(item, constants.API_ATTR_HISTORY_ITEM_ID, constants.EMPTY_TEXT),
			constants.KEY_DATE: str(date_value),
			constants.KEY_TYPE: str(_get_attribute(item, constants.API_ATTR_TYPE, constants.EMPTY_TEXT)),
			constants.KEY_VOICE: str(_get_attribute(item, constants.API_ATTR_VOICE_NAME, constants.EMPTY_TEXT)),
			constants.KEY_MODEL: str(_get_attribute(item, constants.API_ATTR_MODEL_ID, constants.EMPTY_TEXT)),
			constants.KEY_PREVIEW: str(_get_attribute(item, constants.API_ATTR_TEXT, constants.EMPTY_TEXT)),
		})
	return history_items


def get_history_audio(history_item_id):
	client = get_client()
	response = _call_sdk(
		_get_sdk_method(client, constants.API_ATTR_HISTORY, constants.API_ATTR_GET_AUDIO),
		{constants.API_KW_HISTORY_ITEM_ID: history_item_id},
	)
	return _join_audio_chunks(response)


def delete_history_item(history_item_id):
	client = get_client()
	_call_sdk(
		_get_sdk_method(client, constants.API_ATTR_HISTORY, constants.API_ATTR_DELETE),
		{constants.API_KW_HISTORY_ITEM_ID: history_item_id},
	)


def get_pronunciation_dictionaries():
	client = get_client()
	pronunciation_client = getattr(client, constants.API_ATTR_PRONUNCIATION, None)
	if pronunciation_client is None:
		pronunciation_client = getattr(client, constants.API_ATTR_PRONUNCIATION_DICTIONARY, None)
	if pronunciation_client is None:
		raise ElevenDeskAPIError(constants.ERROR_SDK_RESPONSE)
	response = _call_sdk(
		getattr(pronunciation_client, constants.API_ATTR_GET_ALL),
		{},
	)
	dictionaries = []
	for item in _get_collection(response, constants.API_ATTR_DICTIONARIES):
		dictionaries.append({
			constants.KEY_ID: _get_attribute(item, constants.API_ATTR_ID, constants.EMPTY_TEXT),
			constants.KEY_NAME: _get_attribute(item, constants.API_ATTR_NAME, constants.EMPTY_TEXT),
			constants.KEY_DESCRIPTION: _get_attribute(item, constants.API_ATTR_DESCRIPTION, constants.EMPTY_TEXT) or constants.EMPTY_TEXT,
		})
	return dictionaries
