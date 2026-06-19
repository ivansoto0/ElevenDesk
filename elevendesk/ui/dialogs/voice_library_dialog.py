import threading

import wx

from elevendesk import api
from elevendesk import constants


class VoiceLibraryDialog(wx.Dialog):
	def __init__(self, parent, tts_panel):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_VOICE_LIBRARY, size=constants.DIALOG_SIZE)
		self.tts_panel = tts_panel
		self.voices = []
		self.visible_voices = []
		self.search_label = wx.StaticText(self, label=constants.LABEL_SEARCH)
		self.search_input = wx.TextCtrl(self, name=constants.LABEL_SEARCH)
		self.voice_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name=constants.TITLE_VOICE_LIBRARY)
		self.voice_list.InsertColumn(constants.COLUMN_INDEX_NAME, constants.COLUMN_NAME, width=constants.COLUMN_WIDTH_NAME)
		self.voice_list.InsertColumn(constants.COLUMN_INDEX_CATEGORY, constants.COLUMN_CATEGORY, width=constants.COLUMN_WIDTH_CATEGORY)
		self.voice_list.InsertColumn(constants.COLUMN_INDEX_DESCRIPTION, constants.COLUMN_DESCRIPTION, width=constants.COLUMN_WIDTH_DESCRIPTION)
		self.use_label = wx.StaticText(self, label=constants.LABEL_USE_VOICE)
		self.use_button = wx.Button(self, label=constants.LABEL_USE_VOICE, name=constants.LABEL_USE_VOICE)
		self.use_button.Disable()
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		self._layout_controls()
		self.search_input.Bind(wx.EVT_TEXT, self._on_search)
		self.voice_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection)
		self.use_button.Bind(wx.EVT_BUTTON, self._on_use)
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.search_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.search_input, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.voice_list, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
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
		self.visible_voices = []
		for voice in self.voices:
			searchable_text = constants.SPACE.join((
				voice[constants.KEY_NAME],
				voice[constants.KEY_CATEGORY],
				voice[constants.KEY_DESCRIPTION],
			)).lower()
			if search_text in searchable_text:
				self.visible_voices.append(voice)
		self.voice_list.DeleteAllItems()
		for voice in self.visible_voices:
			row = self.voice_list.InsertItem(self.voice_list.GetItemCount(), voice[constants.KEY_NAME])
			self.voice_list.SetItem(row, constants.COLUMN_INDEX_CATEGORY, voice[constants.KEY_CATEGORY])
			self.voice_list.SetItem(row, constants.COLUMN_INDEX_DESCRIPTION, voice[constants.KEY_DESCRIPTION])
		self.use_button.Disable()

	def _on_selection(self, event):
		self.use_button.Enable()

	def _on_use(self, event):
		selected_index = self.voice_list.GetFirstSelected()
		if selected_index == wx.NOT_FOUND:
			return
		voice_id = self.visible_voices[selected_index][constants.KEY_VOICE_ID]
		self.tts_panel.refresh_voices(voice_id)
		self.Destroy()
