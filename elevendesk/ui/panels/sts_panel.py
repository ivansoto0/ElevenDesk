import threading

import wx

from elevendesk import api
from elevendesk import config
from elevendesk import constants
from elevendesk import playback
from elevendesk.ui import choices


class SpeechToSpeechPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.voices = []
		self.selected_file_path = constants.EMPTY_TEXT
		self.last_audio = None
		self.last_output_format = constants.DEFAULT_OUTPUT_FORMAT
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()
		self._apply_defaults()
		self.refresh_voices()

	def _create_controls(self):
		self.open_button_label = wx.StaticText(self, label=constants.LABEL_OPEN_AUDIO)
		self.open_button = wx.Button(
			self,
			label=constants.LABEL_OPEN_AUDIO,
			name=constants.NAME_OPEN_STS_AUDIO,
		)
		self.selected_file_label = wx.StaticText(self, label=constants.LABEL_SELECTED_FILE)
		self.selected_file = wx.TextCtrl(
			self,
			style=wx.TE_READONLY,
			name=constants.NAME_SELECTED_STS_FILE,
		)
		self.voice_label = wx.StaticText(self, label=constants.LABEL_VOICE)
		self.voice_combo = choices.create_choice(self, name=constants.LABEL_VOICE)
		self.model_label = wx.StaticText(self, label=constants.LABEL_MODEL)
		self.model_combo = choices.create_choice(
			self,
			choices=list(constants.MODEL_STS_IDS),
			name=constants.LABEL_MODEL,
		)
		self.output_format_label = wx.StaticText(self, label=constants.LABEL_OUTPUT_FORMAT)
		self.output_format_combo = choices.create_choice(
			self,
			choices=list(constants.OUTPUT_FORMATS),
			name=constants.LABEL_OUTPUT_FORMAT,
		)
		self.convert_button = wx.Button(
			self,
			label=constants.LABEL_CONVERT,
			name=constants.NAME_CONVERT_STS,
		)
		self.convert_button.Disable()
		self.play_button = wx.Button(
			self,
			label=constants.LABEL_PLAY,
			name=constants.NAME_PLAY_STS_AUDIO,
		)
		self.save_button = wx.Button(
			self,
			label=constants.LABEL_SAVE,
			name=constants.NAME_SAVE_STS_AUDIO,
		)
		self.play_button.Disable()
		self.save_button.Disable()
		self.status_text = wx.StaticText(self, label=constants.STATUS_READY, name=constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.open_button_label, self.open_button),
			(self.selected_file_label, self.selected_file),
			(self.voice_label, self.voice_combo),
			(self.model_label, self.model_combo),
			(self.output_format_label, self.output_format_combo),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			main_sizer.Add(control, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		action_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for button in (self.convert_button, self.play_button, self.save_button):
			action_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.CONTROL_GAP)
		main_sizer.Add(action_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _set_tab_order(self):
		controls = (
			self.open_button,
			self.selected_file,
			self.voice_combo,
			self.model_combo,
			self.output_format_combo,
			self.convert_button,
			self.play_button,
			self.save_button,
		)
		for i in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[i].MoveAfterInTabOrder(controls[i - constants.INDEX_STEP])

	def _bind_events(self):
		self.open_button.Bind(wx.EVT_BUTTON, self._on_open)
		self.convert_button.Bind(wx.EVT_BUTTON, self._on_convert)
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)

	def _apply_defaults(self):
		settings = config.load_config()
		self._select_combo(self.model_combo, settings.get(constants.KEY_DEFAULT_MODEL, constants.MODEL_STS_MULTILINGUAL_V2))
		self._select_combo(self.output_format_combo, settings[constants.KEY_DEFAULT_OUTPUT_FORMAT])
		if self.model_combo.GetSelection() == wx.NOT_FOUND and self.model_combo.GetCount():
			self.model_combo.SetSelection(constants.FIRST_ITEM_INDEX)

	def _select_combo(self, combo, value):
		selection = combo.FindString(value)
		if selection == wx.NOT_FOUND and combo.GetCount():
			selection = constants.FIRST_ITEM_INDEX
		if selection != wx.NOT_FOUND:
			combo.SetSelection(selection)

	def refresh_voices(self, preferred_voice_id=None):
		self.status_text.SetLabel(constants.STATUS_LOADING_VOICES)
		threading.Thread(
			target=self._load_voices_worker,
			args=(preferred_voice_id,),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _load_voices_worker(self, preferred_voice_id):
		try:
			voices = api.get_voices()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(self._set_voices, voices, preferred_voice_id)

	def _set_voices(self, voices, preferred_voice_id):
		self.voices = voices
		self.voice_combo.Clear()
		for voice in voices:
			self.voice_combo.Append(voice[constants.KEY_NAME])
		settings = config.load_config()
		target_voice_id = preferred_voice_id or settings[constants.KEY_DEFAULT_VOICE_ID]
		for index, voice in enumerate(self.voices):
			if voice[constants.KEY_VOICE_ID] == target_voice_id:
				self.voice_combo.SetSelection(index)
				break
		if self.voice_combo.GetSelection() == wx.NOT_FOUND and self.voice_combo.GetCount():
			self.voice_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.status_text.SetLabel(constants.STATUS_READY)

	def _on_open(self, event):
		with wx.FileDialog(
			self,
			message=constants.TITLE_SELECT_AUDIO,
			wildcard=constants.AUDIO_FILE_WILDCARD,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			self.selected_file_path = dialog.GetPath()
		self.selected_file.SetValue(self.selected_file_path)
		self.convert_button.Enable()

	def _on_convert(self, event):
		if not self.selected_file_path:
			self.status_text.SetLabel(constants.ERROR_AUDIO_REQUIRED)
			return
		voice_index = self.voice_combo.GetSelection()
		if voice_index == wx.NOT_FOUND:
			self.status_text.SetLabel(constants.ERROR_VOICE_REQUIRED)
			return
		voice_id = self.voices[voice_index][constants.KEY_VOICE_ID]
		model_id = self.model_combo.GetStringSelection()
		output_format = self.output_format_combo.GetStringSelection()
		self.convert_button.Disable()
		self.status_text.SetLabel(constants.STATUS_CONVERTING)
		threading.Thread(
			target=self._convert_worker,
			args=(self.selected_file_path, voice_id, model_id, output_format),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _convert_worker(self, file_path, voice_id, model_id, output_format):
		try:
			with open(file_path, constants.FILE_MODE_BINARY_READ) as audio_file:
				audio_bytes = audio_file.read()
			result = api.speech_to_speech(audio_bytes, voice_id, model_id, output_format)
		except (OSError, api.ElevenDeskAPIError) as error:
			wx.CallAfter(self._conversion_failed, str(error))
			return
		wx.CallAfter(self._conversion_succeeded, result, output_format)

	def _conversion_succeeded(self, audio_bytes, output_format):
		self.last_audio = audio_bytes
		self.last_output_format = output_format
		self.convert_button.Enable()
		self.play_button.Enable()
		self.save_button.Enable()
		playback.play_audio(self.last_audio, self.last_output_format)
		self.status_text.SetLabel(constants.STATUS_PLAYING)

	def _conversion_failed(self, message):
		self.convert_button.Enable()
		self.status_text.SetLabel(message)

	def _on_play(self, event):
		if self.last_audio:
			playback.play_audio(self.last_audio, self.last_output_format)
			self.status_text.SetLabel(constants.STATUS_PLAYING)

	def _on_save(self, event):
		self.save_last_output()

	def save_last_output(self, parent=None):
		if not self.last_audio:
			return False
		parent = parent or self
		extension, wildcard = constants.OUTPUT_FILE_OPTIONS.get(
			self.last_output_format,
			constants.DEFAULT_OUTPUT_FILE_OPTION,
		)
		default_file = constants.DEFAULT_AUDIO_BASENAME + extension
		output_directory = config.load_config()[constants.KEY_OUTPUT_DIRECTORY]
		with wx.FileDialog(
			parent,
			message=constants.TITLE_SAVE_AUDIO,
			defaultDir=output_directory,
			defaultFile=default_file,
			wildcard=wildcard,
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return False
			file_path = dialog.GetPath()
		try:
			with open(file_path, constants.FILE_MODE_BINARY_WRITE) as output_file:
				output_file.write(self.last_audio)
		except OSError as error:
			self.status_text.SetLabel(str(error))
			return False
		self.status_text.SetLabel(constants.STATUS_SAVED + file_path)
		return True

	def get_last_output(self):
		return self.last_audio, self.last_output_format
