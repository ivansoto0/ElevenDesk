import threading

import wx
from smart_list import Column, SmartList

from elevendesk import api
from elevendesk import constants


class PronunciationDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_PRONUNCIATION, size=constants.DIALOG_SIZE)
		self.dictionary_list = SmartList(parent=self, name=constants.TITLE_PRONUNCIATION)
		self.dictionary_list.set_columns([
			Column(constants.COLUMN_NAME, constants.COLUMN_WIDTH_NAME, constants.KEY_NAME),
			Column(constants.COLUMN_ID, constants.COLUMN_WIDTH_ID, constants.KEY_ID),
			Column(constants.COLUMN_DESCRIPTION, constants.COLUMN_WIDTH_DESCRIPTION, constants.KEY_DESCRIPTION),
		])
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.dictionary_list.control.control, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
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
		self.dictionary_list.add_items(dictionaries)
		self.status_text.SetLabel(constants.STATUS_READY)
