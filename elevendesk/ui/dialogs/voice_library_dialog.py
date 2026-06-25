import threading

import wx
from smart_list import Column, SmartList

from elevendesk import api
from elevendesk import constants


class VoiceLibraryDialog(wx.Dialog):
	def __init__(self, parent, tts_panel):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_VOICE_LIBRARY, size=constants.DIALOG_SIZE)
		self.tts_panel = tts_panel
		self.voices = []
		self.search_label = wx.StaticText(self, label=constants.LABEL_SEARCH)
		self.search_input = wx.TextCtrl(self, name=constants.LABEL_SEARCH)
		self.voice_list = SmartList(parent=self, name=constants.TITLE_VOICE_LIBRARY)
		self.voice_list.set_columns([
			Column(constants.COLUMN_NAME, constants.COLUMN_WIDTH_NAME, constants.KEY_NAME),
			Column(constants.COLUMN_CATEGORY, constants.COLUMN_WIDTH_CATEGORY, constants.KEY_CATEGORY),
			Column(constants.COLUMN_DESCRIPTION, constants.COLUMN_WIDTH_DESCRIPTION, constants.KEY_DESCRIPTION),
		])
		self.use_label = wx.StaticText(self, label=constants.LABEL_USE_VOICE)
		self.use_button = wx.Button(self, label=constants.LABEL_USE_VOICE, name=constants.LABEL_USE_VOICE)
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		self._layout_controls()
		self.search_input.Bind(wx.EVT_TEXT, self._on_search)
		self.use_button.Bind(wx.EVT_BUTTON, self._on_use)
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.search_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.search_input, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.voice_list.control.control, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer.Add(self.use_label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
		button_sizer.Add(self.use_button, constants.SIZER_PROPORTION_NONE)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _load_worker(self):
		try:
			voices = api.get_voices()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(self._set_voices, voices)

	def _set_voices(self, voices):
		self.voices = voices
		self._filter_voices()
		self.status_text.SetLabel(constants.STATUS_READY)

	def _on_search(self, event):
		self._filter_voices()

	def _filter_voices(self):
		search_text = self.search_input.GetValue().lower()
		visible = []
		for voice in self.voices:
			searchable_text = constants.SPACE.join((
				voice[constants.KEY_NAME],
				voice[constants.KEY_CATEGORY],
				voice[constants.KEY_DESCRIPTION],
			)).lower()
			if search_text in searchable_text:
				visible.append(voice)
		self.voice_list.clear()
		self.voice_list.add_items(visible)

	def _on_use(self, event):
		voice = self.voice_list.get_selected_item()
		if voice is None:
			self.status_text.SetLabel(constants.ERROR_SELECTION_REQUIRED)
			return
		self.tts_panel.refresh_voices(voice[constants.KEY_VOICE_ID])
		self.Destroy()
