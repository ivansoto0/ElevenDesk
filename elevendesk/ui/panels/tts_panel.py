import threading

import wx

from elevendesk import api
from elevendesk import config
from elevendesk import constants
from elevendesk import playback


class TextToSpeechPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.voices = []
		self.last_audio = None
		self.last_output_format = constants.DEFAULT_OUTPUT_FORMAT
		self._create_controls()
		self._bind_events()
		self._layout_controls()
		self._set_tab_order()
		self._apply_defaults()
		self.refresh_voices()

	def _create_controls(self):
		self.voice_label = wx.StaticText(self, label=constants.LABEL_VOICE)
		self.voice_combo = wx.ComboBox(self, style=wx.CB_READONLY, name=constants.LABEL_VOICE)
		self.model_label = wx.StaticText(self, label=constants.LABEL_MODEL)
		self.model_combo = wx.ComboBox(
			self,
			choices=list(constants.MODEL_IDS),
			style=wx.CB_READONLY,
			name=constants.LABEL_MODEL,
		)
		self.output_format_label = wx.StaticText(self, label=constants.LABEL_OUTPUT_FORMAT)
		self.output_format_combo = wx.ComboBox(
			self,
			choices=list(constants.OUTPUT_FORMATS),
			style=wx.CB_READONLY,
			name=constants.LABEL_OUTPUT_FORMAT,
		)
		self.text_label = wx.StaticText(self, label=constants.LABEL_TEXT)
		self.text_input = wx.TextCtrl(self, style=wx.TE_MULTILINE, name=constants.LABEL_TEXT)
		self.text_input.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.TEXT_MIN_HEIGHT))
		self.stability_label, self.stability_slider, self.stability_value = self._create_slider(
			constants.LABEL_STABILITY,
			constants.SLIDER_MINIMUM,
			constants.SLIDER_MAXIMUM,
			constants.SLIDER_DEFAULT_STABILITY,
		)
		self.similarity_label, self.similarity_slider, self.similarity_value = self._create_slider(
			constants.LABEL_SIMILARITY,
			constants.SLIDER_MINIMUM,
			constants.SLIDER_MAXIMUM,
			constants.SLIDER_DEFAULT_SIMILARITY,
		)
		self.style_label, self.style_slider, self.style_value = self._create_slider(
			constants.LABEL_STYLE,
			constants.SLIDER_MINIMUM,
			constants.SLIDER_MAXIMUM,
			constants.SLIDER_DEFAULT_STYLE,
		)
		self.speed_label, self.speed_slider, self.speed_value = self._create_slider(
			constants.LABEL_SPEED,
			constants.SLIDER_SPEED_MINIMUM,
			constants.SLIDER_SPEED_MAXIMUM,
			constants.SLIDER_SPEED_DEFAULT,
		)
		self.speed_slider.SetName(
			constants.SPEED_ACCESSIBLE_NAME_TEMPLATE.format(
				constants.LABEL_SPEED,
				constants.SLIDER_SPEED_DEFAULT / constants.SLIDER_SPEED_DIVISOR,
			)
		)
		self.speed_value.SetLabel(
			constants.SPEED_VALUE_TEMPLATE.format(
				constants.LABEL_SPEED,
				constants.SLIDER_SPEED_DEFAULT / constants.SLIDER_SPEED_DIVISOR,
			)
		)
		self.generate_button = wx.Button(
			self,
			label=constants.LABEL_GENERATE,
			name=constants.NAME_GENERATE_SPEECH_SHORTCUT,
		)
		self.play_button = wx.Button(self, label=constants.LABEL_PLAY, name=constants.NAME_PLAY_GENERATED_SPEECH)
		self.save_button = wx.Button(self, label=constants.LABEL_SAVE, name=constants.NAME_SAVE_GENERATED_SPEECH)
		self.play_button.Disable()
		self.save_button.Disable()
		self.status_text = wx.StaticText(self, label=constants.STATUS_READY, name=constants.LABEL_STATUS)

	def _create_slider(self, label, minimum, maximum, value):
		slider_label = wx.StaticText(self, label=label)
		slider = wx.Slider(
			self,
			value=value,
			minValue=minimum,
			maxValue=maximum,
			name=constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(label, value),
		)
		value_label = wx.StaticText(self, label=constants.SLIDER_VALUE_TEMPLATE.format(label, value))
		return slider_label, slider, value_label

	def _bind_events(self):
		self.generate_button.Bind(wx.EVT_BUTTON, self._on_generate)
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)
		self.voice_combo.Bind(wx.EVT_COMBOBOX, self._on_voice_selected)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key_hook)
		for slider in (
			self.stability_slider,
			self.similarity_slider,
			self.style_slider,
			self.speed_slider,
		):
			slider.Bind(wx.EVT_SLIDER, self._on_slider)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.text_label, self.text_input),
			(self.model_label, self.model_combo),
			(self.output_format_label, self.output_format_combo),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.text_input else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		settings_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, constants.LABEL_VOICE_SETTINGS)
		for slider_label, slider, value_label in (
			(self.stability_label, self.stability_slider, self.stability_value),
			(self.similarity_label, self.similarity_slider, self.similarity_value),
			(self.style_label, self.style_slider, self.style_value),
			(self.speed_label, self.speed_slider, self.speed_value),
		):
			settings_sizer.Add(slider_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			settings_sizer.Add(slider, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
			settings_sizer.Add(value_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(settings_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		action_sizer = wx.BoxSizer(wx.HORIZONTAL)
		action_sizer.Add(self.voice_label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
		action_sizer.Add(self.voice_combo, constants.SIZER_PROPORTION_EXPAND, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.SECTION_GAP)
		for button in (self.generate_button, self.play_button, self.save_button):
			action_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.CONTROL_GAP)
		main_sizer.Add(action_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)
		main_sizer.SetSizeHints(self)

	def _set_tab_order(self):
		controls = (
			self.text_input,
			self.model_combo,
			self.output_format_combo,
			self.stability_slider,
			self.similarity_slider,
			self.style_slider,
			self.speed_slider,
			self.voice_combo,
			self.generate_button,
			self.play_button,
			self.save_button,
		)
		for control_index in range(constants.FIRST_ITEM_INDEX + constants.INDEX_STEP, len(controls)):
			controls[control_index].MoveAfterInTabOrder(controls[control_index - constants.INDEX_STEP])

	def focus_text_input(self):
		self.text_input.SetFocus()

	def _apply_defaults(self):
		settings = config.load_config()
		self._select_combo(self.model_combo, settings[constants.KEY_DEFAULT_MODEL])
		self._select_combo(self.output_format_combo, settings[constants.KEY_DEFAULT_OUTPUT_FORMAT])

	def _select_combo(self, combo, value):
		selection = combo.FindString(value)
		if selection == wx.NOT_FOUND and combo.GetCount():
			selection = constants.FIRST_ITEM_INDEX
		if selection != wx.NOT_FOUND:
			combo.SetSelection(selection)

	def _on_slider(self, event):
		slider = event.GetEventObject()
		value = slider.GetValue()
		if slider is self.speed_slider:
			speed_value = value / constants.SLIDER_SPEED_DIVISOR
			self.speed_value.SetLabel(
				constants.SPEED_VALUE_TEMPLATE.format(constants.LABEL_SPEED, speed_value)
			)
			slider.SetName(constants.SPEED_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_SPEED, speed_value))
		elif slider is self.stability_slider:
			self.stability_value.SetLabel(constants.SLIDER_VALUE_TEMPLATE.format(constants.LABEL_STABILITY, value))
			slider.SetName(constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_STABILITY, value))
		elif slider is self.similarity_slider:
			self.similarity_value.SetLabel(constants.SLIDER_VALUE_TEMPLATE.format(constants.LABEL_SIMILARITY, value))
			slider.SetName(constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_SIMILARITY, value))
		else:
			self.style_value.SetLabel(constants.SLIDER_VALUE_TEMPLATE.format(constants.LABEL_STYLE, value))
			slider.SetName(constants.SLIDER_ACCESSIBLE_NAME_TEMPLATE.format(constants.LABEL_STYLE, value))

	def refresh_voices(self, preferred_voice_id=None):
		self.status_text.SetLabel(constants.STATUS_LOADING_VOICES)
		threading.Thread(target=self._load_voices_worker, args=(preferred_voice_id,), daemon=constants.THREAD_DAEMON).start()

	def _load_voices_worker(self, preferred_voice_id):
		try:
			voices = api.get_voices()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._show_voice_error, str(error))
			return
		wx.CallAfter(self._set_voices, voices, preferred_voice_id)

	def _set_voices(self, voices, preferred_voice_id):
		self.voices = voices
		self.voice_combo.Clear()
		for voice in voices:
			self.voice_combo.Append(voice[constants.KEY_NAME])
		settings = config.load_config()
		target_voice_id = preferred_voice_id or settings[constants.KEY_DEFAULT_VOICE_ID]
		self.select_voice_by_id(target_voice_id)
		if self.voice_combo.GetSelection() == wx.NOT_FOUND and self.voice_combo.GetCount():
			self.voice_combo.SetSelection(constants.FIRST_ITEM_INDEX)
		self.status_text.SetLabel(constants.STATUS_READY)

	def _show_voice_error(self, message):
		self.status_text.SetLabel(message)

	def select_voice_by_id(self, voice_id):
		for index, voice in enumerate(self.voices):
			if voice[constants.KEY_VOICE_ID] == voice_id:
				self.voice_combo.SetSelection(index)
				return True
		return False

	def _on_voice_selected(self, event):
		voice_index = self.voice_combo.GetSelection()
		if voice_index == wx.NOT_FOUND:
			return
		self._save_voice_id(self.voices[voice_index][constants.KEY_VOICE_ID])

	def _save_voice_id(self, voice_id):
		settings = config.load_config()
		settings[constants.KEY_DEFAULT_VOICE_ID] = voice_id
		try:
			config.save_config(settings)
		except OSError as error:
			self.status_text.SetLabel(str(error))

	def _on_generate(self, event):
		self._start_generation()

	def _on_key_hook(self, event):
		key_code = event.GetKeyCode()
		is_return = key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER)
		if event.ControlDown() and is_return and self.generate_button.IsEnabled():
			self._start_generation()
			return
		event.Skip()

	def _start_generation(self):
		text = self.text_input.GetValue().strip()
		voice_index = self.voice_combo.GetSelection()
		if not text:
			self.status_text.SetLabel(constants.ERROR_TEXT_REQUIRED)
			return
		if voice_index == wx.NOT_FOUND:
			self.status_text.SetLabel(constants.ERROR_VOICE_REQUIRED)
			return
		voice_id = self.voices[voice_index][constants.KEY_VOICE_ID]
		self._save_voice_id(voice_id)
		model_id = self.model_combo.GetStringSelection()
		output_format = self.output_format_combo.GetStringSelection()
		voice_settings = {
			constants.API_KEY_STABILITY: self.stability_slider.GetValue() / constants.PERCENT_DIVISOR,
			constants.API_KEY_SIMILARITY_BOOST: self.similarity_slider.GetValue() / constants.PERCENT_DIVISOR,
			constants.API_KEY_STYLE: self.style_slider.GetValue() / constants.PERCENT_DIVISOR,
			constants.API_KEY_SPEED: self.speed_slider.GetValue() / constants.SLIDER_SPEED_DIVISOR,
		}
		self.generate_button.Disable()
		self.status_text.SetLabel(constants.STATUS_GENERATING)
		threading.Thread(
			target=self._generate_worker,
			args=(text, voice_id, model_id, voice_settings, output_format),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _generate_worker(self, text, voice_id, model_id, voice_settings, output_format):
		try:
			audio_bytes = api.text_to_speech(text, voice_id, model_id, voice_settings, output_format)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._generation_failed, str(error))
			return
		wx.CallAfter(self._generation_succeeded, audio_bytes, output_format)

	def _generation_succeeded(self, audio_bytes, output_format):
		self.last_audio = audio_bytes
		self.last_output_format = output_format
		self.generate_button.Enable()
		self.play_button.Enable()
		self.save_button.Enable()
		playback.play_audio(self.last_audio, self.last_output_format)
		self.status_text.SetLabel(constants.STATUS_PLAYING)

	def _generation_failed(self, message):
		self.generate_button.Enable()
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
