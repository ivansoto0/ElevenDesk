import threading

import wx

from elevendesk import api
from elevendesk import constants
from elevendesk import playback


class SoundEffectsPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.last_audio = None
		self.last_output_format = constants.OUTPUT_MP3_44100_128
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()

	def _create_controls(self):
		self.prompt_label = wx.StaticText(self, label=constants.LABEL_SOUND_PROMPT)
		self.prompt_input = wx.TextCtrl(self, name=constants.LABEL_SOUND_PROMPT)
		self.duration_label = wx.StaticText(self, label=constants.LABEL_DURATION)
		self.duration_input = wx.SpinCtrlDouble(
			self,
			min=constants.DURATION_MINIMUM,
			max=constants.DURATION_MAXIMUM,
			initial=constants.DURATION_DEFAULT,
			inc=constants.DURATION_INCREMENT,
			name=constants.LABEL_DURATION,
		)
		self.duration_input.SetDigits(constants.SPIN_DIGITS)
		self.generate_label = wx.StaticText(self, label=constants.LABEL_GENERATE)
		self.generate_button = wx.Button(
			self,
			label=constants.LABEL_GENERATE,
			name=constants.NAME_GENERATE_SOUND_EFFECT,
		)
		self.play_label = wx.StaticText(self, label=constants.LABEL_PLAY)
		self.play_button = wx.Button(
			self,
			label=constants.LABEL_PLAY,
			name=constants.NAME_PLAY_GENERATED_SOUND_EFFECT,
		)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(
			self,
			label=constants.LABEL_SAVE,
			name=constants.NAME_SAVE_GENERATED_SOUND_EFFECT,
		)
		self.play_button.Disable()
		self.save_button.Disable()
		self.status_text = wx.StaticText(self, label=constants.STATUS_READY, name=constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.prompt_label, self.prompt_input),
			(self.duration_label, self.duration_input),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			main_sizer.Add(control, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for label, button in (
			(self.generate_label, self.generate_button),
			(self.play_label, self.play_button),
			(self.save_label, self.save_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _set_tab_order(self):
		self.duration_input.MoveAfterInTabOrder(self.prompt_input)
		self.generate_button.MoveAfterInTabOrder(self.duration_input)
		self.play_button.MoveAfterInTabOrder(self.generate_button)
		self.save_button.MoveAfterInTabOrder(self.play_button)

	def _bind_events(self):
		self.generate_button.Bind(wx.EVT_BUTTON, self._on_generate)
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)

	def _on_generate(self, event):
		prompt = self.prompt_input.GetValue().strip()
		if not prompt:
			self.status_text.SetLabel(constants.ERROR_PROMPT_REQUIRED)
			return
		self.generate_button.Disable()
		self.status_text.SetLabel(constants.STATUS_GENERATING_EFFECT)
		threading.Thread(
			target=self._generate_worker,
			args=(prompt, self.duration_input.GetValue()),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _generate_worker(self, prompt, duration):
		try:
			audio_bytes = api.generate_sound_effect(prompt, duration)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._generation_failed, str(error))
			return
		wx.CallAfter(self._generation_succeeded, audio_bytes)

	def _generation_succeeded(self, audio_bytes):
		self.last_audio = audio_bytes
		self.generate_button.Enable()
		self.play_button.Enable()
		self.save_button.Enable()
		self.status_text.SetLabel(constants.STATUS_EFFECT_GENERATED)

	def _generation_failed(self, message):
		self.generate_button.Enable()
		self.status_text.SetLabel(message)

	def _on_play(self, event):
		if self.last_audio:
			playback.play_audio(self.last_audio, self.last_output_format)
			self.status_text.SetLabel(constants.STATUS_PLAYING)

	def _on_save(self, event):
		self.GetTopLevelParent().save_audio_bytes(self.last_audio, self.last_output_format, self.status_text)

	def get_last_output(self):
		return self.last_audio, self.last_output_format
