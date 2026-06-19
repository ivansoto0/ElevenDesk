import json
import os

import wx

from elevendesk import constants


def get_config_path():
	user_data_directory = wx.StandardPaths.Get().GetUserDataDir()
	return os.path.join(user_data_directory, constants.CONFIG_FILE_NAME)


def get_default_settings():
	settings = dict(constants.DEFAULT_SETTINGS)
	if not settings[constants.KEY_OUTPUT_DIRECTORY]:
		settings[constants.KEY_OUTPUT_DIRECTORY] = wx.StandardPaths.Get().GetDocumentsDir()
	return settings


def load_config():
	settings = get_default_settings()
	config_path = get_config_path()
	try:
		with open(config_path, constants.FILE_MODE_BINARY_READ) as config_file:
			loaded_settings = json.load(config_file)
	except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeDecodeError):
		return settings
	if not isinstance(loaded_settings, dict):
		return settings
	for setting_name in settings:
		setting_value = loaded_settings.get(setting_name)
		if isinstance(setting_value, str):
			settings[setting_name] = setting_value
	return settings


def save_config(settings_dict):
	config_path = get_config_path()
	config_directory = os.path.dirname(config_path)
	os.makedirs(config_directory, exist_ok=True)
	with open(config_path, constants.FILE_MODE_TEXT_WRITE, encoding=constants.JSON_ENCODING) as config_file:
		json.dump(settings_dict, config_file, indent=constants.CONTROL_GAP)

