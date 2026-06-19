import threading

import wx

from elevendesk import api
from elevendesk import constants
from elevendesk import playback


class HistoryDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_HISTORY, size=constants.DIALOG_SIZE)
		self.history_items = []
		self.history_list = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, name=constants.TITLE_HISTORY)
		for index, (column_header, column_width) in enumerate((
			(constants.COLUMN_DATE, constants.COLUMN_WIDTH_DATE),
			(constants.COLUMN_TYPE, constants.COLUMN_WIDTH_TYPE),
			(constants.COLUMN_VOICE, constants.COLUMN_WIDTH_VOICE),
			(constants.COLUMN_MODEL, constants.COLUMN_WIDTH_MODEL),
			(constants.COLUMN_PREVIEW, constants.COLUMN_WIDTH_PREVIEW),
		)):
			self.history_list.InsertColumn(index, column_header, width=column_width)
		self.play_label = wx.StaticText(self, label=constants.LABEL_PLAY)
		self.play_button = wx.Button(self, label=constants.LABEL_PLAY, name=constants.LABEL_PLAY)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(self, label=constants.LABEL_SAVE, name=constants.LABEL_SAVE)
		self.delete_label = wx.StaticText(self, label=constants.LABEL_DELETE)
		self.delete_button = wx.Button(self, label=constants.LABEL_DELETE, name=constants.LABEL_DELETE)
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		self._layout_controls()
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)
		self.delete_button.Bind(wx.EVT_BUTTON, self._on_delete)
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.history_list, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for label, button in (
			(self.play_label, self.play_button),
			(self.save_label, self.save_button),
			(self.delete_label, self.delete_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _load_worker(self):
		try:
			items = api.get_history()
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(self._set_items, items)

	def _set_items(self, items):
		self.history_items = items
		self.history_list.DeleteAllItems()
		for item in items:
			preview = item[constants.KEY_PREVIEW][:constants.PREVIEW_MAX_LENGTH]
			row = self.history_list.InsertItem(self.history_list.GetItemCount(), item[constants.KEY_DATE])
			self.history_list.SetItem(row, constants.COLUMN_INDEX_TYPE, item[constants.KEY_TYPE])
			self.history_list.SetItem(row, constants.COLUMN_INDEX_VOICE, item[constants.KEY_VOICE])
			self.history_list.SetItem(row, constants.COLUMN_INDEX_MODEL, item[constants.KEY_MODEL])
			self.history_list.SetItem(row, constants.COLUMN_INDEX_PREVIEW, preview)
		self.status_text.SetLabel(constants.STATUS_READY)

	def _selected_item(self):
		index = self.history_list.GetFirstSelected()
		if index == wx.NOT_FOUND:
			self.status_text.SetLabel(constants.ERROR_SELECTION_REQUIRED)
			return None
		return self.history_items[index]

	def _on_play(self, event):
		item = self._selected_item()
		if item:
			threading.Thread(target=self._play_worker, args=(item,), daemon=constants.THREAD_DAEMON).start()

	def _play_worker(self, item):
		try:
			audio_bytes = api.get_history_audio(item[constants.KEY_HISTORY_ITEM_ID])
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		playback.play_audio(audio_bytes, constants.OUTPUT_MP3_44100_128)
		wx.CallAfter(self.status_text.SetLabel, constants.STATUS_PLAYING)

	def _on_save(self, event):
		item = self._selected_item()
		if item:
			threading.Thread(target=self._save_worker, args=(item,), daemon=constants.THREAD_DAEMON).start()

	def _save_worker(self, item):
		try:
			audio_bytes = api.get_history_audio(item[constants.KEY_HISTORY_ITEM_ID])
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(
			self.GetParent().save_audio_bytes,
			audio_bytes,
			constants.OUTPUT_MP3_44100_128,
			self.status_text,
		)

	def _on_delete(self, event):
		item = self._selected_item()
		if item:
			threading.Thread(target=self._delete_worker, args=(item,), daemon=constants.THREAD_DAEMON).start()

	def _delete_worker(self, item):
		try:
			api.delete_history_item(item[constants.KEY_HISTORY_ITEM_ID])
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(self._remove_item, item)

	def _remove_item(self, item):
		self.history_items.remove(item)
		self._set_items(self.history_items)
