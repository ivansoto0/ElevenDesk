import threading

import wx

from elevendesk import api
from elevendesk import constants


class PronunciationDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_PRONUNCIATION, size=constants.DIALOG_SIZE)
		self.dictionary_list = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
			name=constants.TITLE_PRONUNCIATION,
		)
		self.dictionary_list.InsertColumn(constants.COLUMN_INDEX_NAME, constants.COLUMN_NAME, width=constants.COLUMN_WIDTH_NAME)
		self.dictionary_list.InsertColumn(constants.COLUMN_INDEX_CATEGORY, constants.COLUMN_ID, width=constants.COLUMN_WIDTH_ID)
		self.dictionary_list.InsertColumn(constants.COLUMN_INDEX_DESCRIPTION, constants.COLUMN_DESCRIPTION, width=constants.COLUMN_WIDTH_DESCRIPTION)
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.dictionary_list, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _load_worker(self):
		try:
			dictionaries = api.get_pronunciation_dictionaries()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(self._set_dictionaries, dictionaries)

	def _set_dictionaries(self, dictionaries):
		for item in dictionaries:
			row = self.dictionary_list.InsertItem(self.dictionary_list.GetItemCount(), item[constants.KEY_NAME])
			self.dictionary_list.SetItem(row, constants.COLUMN_INDEX_CATEGORY, item[constants.KEY_ID])
			self.dictionary_list.SetItem(row, constants.COLUMN_INDEX_DESCRIPTION, item[constants.KEY_DESCRIPTION])
		self.status_text.SetLabel(constants.STATUS_READY)
