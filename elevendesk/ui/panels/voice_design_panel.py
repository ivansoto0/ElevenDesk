import threading

import wx

from elevendesk import api
from elevendesk import constants


class VoiceDesignPanel(wx.Panel):
	def __init__(self, parent, tts_panel):
		wx.Panel.__init__(self, parent)
		self.tts_panel = tts_panel
		self.designed_voice = None
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()

	def _create_controls(self):
		self.description_label = wx.StaticText(self, label=constants.LABEL_VOICE_DESCRIPTION)
		self.description_input = wx.TextCtrl(self, style=wx.TE_MULTILINE, name=constants.LABEL_VOICE_DESCRIPTION)
		self.description_input.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.TEXT_MIN_HEIGHT))
		self.name_label = wx.StaticText(self, label=constants.LABEL_VOICE_NAME)
		self.name_input = wx.TextCtrl(self, name=constants.LABEL_VOICE_NAME)
		self.design_label = wx.StaticText(self, label=constants.LABEL_DESIGN_VOICE)
		self.design_button = wx.Button(
			self,
			label=constants.LABEL_DESIGN_VOICE,
			name=constants.NAME_DESIGN_NEW_VOICE,
		)
		self.result_label = wx.StaticText(self, label=constants.LABEL_RESULT)
		self.result_output = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			name=constants.NAME_VOICE_DESIGN_RESULT,
		)
		self.result_output.SetMinSize((constants.DEFAULT_SIZE_WIDTH, constants.RESULT_MIN_HEIGHT))
		self.add_label = wx.StaticText(self, label=constants.LABEL_ADD_TO_VOICE_LIST)
		self.add_button = wx.Button(
			self,
			label=constants.LABEL_ADD_TO_VOICE_LIST,
			name=constants.NAME_ADD_DESIGNED_VOICE,
		)
		self.add_button.Disable()
		self.status_text = wx.StaticText(self, label=constants.STATUS_READY, name=constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.description_label, self.description_input),
			(self.name_label, self.name_input),
			(self.design_label, self.design_button),
			(self.result_label, self.result_output),
			(self.add_label, self.add_button),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.description_input else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _set_tab_order(self):
		self.name_input.MoveAfterInTabOrder(self.description_input)
		self.design_button.MoveAfterInTabOrder(self.name_input)
		self.result_output.MoveAfterInTabOrder(self.design_button)
		self.add_button.MoveAfterInTabOrder(self.result_output)

	def _bind_events(self):
		self.design_button.Bind(wx.EVT_BUTTON, self._on_design)
		self.add_button.Bind(wx.EVT_BUTTON, self._on_add)

	def _on_design(self, event):
		description = self.description_input.GetValue().strip()
		name = self.name_input.GetValue().strip()
		if not description:
			self.status_text.SetLabel(constants.ERROR_VOICE_DESCRIPTION_REQUIRED)
			return
		if not name:
			self.status_text.SetLabel(constants.ERROR_VOICE_NAME_REQUIRED)
			return
		self.design_button.Disable()
		self.status_text.SetLabel(constants.STATUS_DESIGNING_VOICE)
		threading.Thread(
			target=self._design_worker,
			args=(description, name),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _design_worker(self, description, name):
		try:
			voice = api.design_voice(description, name)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._design_failed, str(error))
			return
		wx.CallAfter(self._design_succeeded, voice)

	def _design_succeeded(self, voice):
		self.designed_voice = voice
		self.design_button.Enable()
		self.add_button.Enable()
		self.result_output.SetValue(
			constants.VOICE_RESULT_TEMPLATE.format(
				voice[constants.KEY_NAME],
				voice[constants.KEY_VOICE_ID],
			)
		)
		self.status_text.SetLabel(constants.STATUS_VOICE_DESIGNED)

	def _design_failed(self, message):
		self.design_button.Enable()
		self.status_text.SetLabel(message)

	def _on_add(self, event):
		self.tts_panel.refresh_voices(self.designed_voice[constants.KEY_VOICE_ID])
		self.status_text.SetLabel(constants.STATUS_VOICES_REFRESHED)
