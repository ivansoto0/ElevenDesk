import threading

import wx
from smart_list import Column, SmartList

from elevendesk import api
from elevendesk import constants
from elevendesk import playback


class HistoryDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_HISTORY, size=constants.DIALOG_SIZE)
		self.playback_item_id = None
		self.playback_is_paused = None
		self.playback_request_id = 0
		self.audio_cache = {}
		self.history_list = SmartList(parent=self, name=constants.TITLE_HISTORY)
		self.history_list.set_columns([
			Column(constants.COLUMN_DATE, constants.COLUMN_WIDTH_DATE, constants.KEY_DATE),
			Column(constants.COLUMN_TYPE, constants.COLUMN_WIDTH_TYPE, constants.KEY_TYPE),
			Column(constants.COLUMN_VOICE, constants.COLUMN_WIDTH_VOICE, constants.KEY_VOICE),
			Column(constants.COLUMN_MODEL, constants.COLUMN_WIDTH_MODEL, constants.KEY_MODEL),
			Column(constants.COLUMN_PREVIEW, constants.COLUMN_WIDTH_PREVIEW,
				lambda item: item[constants.KEY_PREVIEW][:constants.PREVIEW_MAX_LENGTH]),
		])
		self.play_label = wx.StaticText(self, label=constants.LABEL_PLAY)
		self.play_button = wx.Button(self, label=constants.LABEL_PLAY, name=constants.LABEL_PLAY)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(self, label=constants.LABEL_SAVE, name=constants.LABEL_SAVE)
		self.delete_label = wx.StaticText(self, label=constants.LABEL_DELETE)
		self.delete_button = wx.Button(self, label=constants.LABEL_DELETE, name=constants.LABEL_DELETE)
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		self._layout_controls()
		self.play_button.SetDefault()
		self.play_button.Bind(wx.EVT_BUTTON, self._on_play)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)
		self.delete_button.Bind(wx.EVT_BUTTON, self._on_delete)
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.history_list.control.control, constants.SIZER_PROPORTION_EXPAND, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
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
		self.history_list.clear()
		self.history_list.add_items(items)
		self.status_text.SetLabel(constants.STATUS_READY)

	def _selected_item(self):
		item = self.history_list.get_selected_item()
		if item is None:
			self.status_text.SetLabel(constants.ERROR_SELECTION_REQUIRED)
		return item

	def _on_play(self, event):
		item = self._selected_item()
		if not item:
			return
		item_id = item[constants.KEY_HISTORY_ITEM_ID]
		if item_id == self.playback_item_id:
			if self.playback_is_paused is False:
				if playback.pause_audio():
					self._set_playback_state(is_paused=True)
				return
			if self.playback_is_paused is True:
				if playback.resume_audio():
					self._set_playback_state(is_paused=False)
				return
		self.playback_request_id += 1
		request_id = self.playback_request_id
		self.playback_item_id = item_id
		self.playback_is_paused = None
		playback.stop_audio()
		self.play_button.Disable()
		self.play_button.SetLabel(constants.LABEL_PLAY)
		self.play_button.SetName(constants.LABEL_PLAY)
		self.status_text.SetLabel(constants.STATUS_LOADING_AUDIO)
		if item_id in self.audio_cache:
			self._start_playback(request_id, item_id, self.audio_cache[item_id])
			return
		threading.Thread(
			target=self._play_worker,
			args=(request_id, item_id),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _play_worker(self, request_id, item_id):
		try:
			audio_bytes = api.get_history_audio(item_id)
		except api.ElevenDeskAPIError as error:
			wx.CallAfter(self._playback_failed, request_id, str(error))
			return
		wx.CallAfter(self._start_playback, request_id, item_id, audio_bytes)

	def _start_playback(self, request_id, item_id, audio_bytes):
		if request_id != self.playback_request_id:
			return
		self.audio_cache[item_id] = audio_bytes
		playback.play_audio(
			audio_bytes,
			constants.OUTPUT_MP3_44100_128,
			on_finished=lambda: wx.CallAfter(self._playback_finished, request_id),
		)
		self._set_playback_state(is_paused=False)

	def _set_playback_state(self, is_paused):
		self.playback_is_paused = is_paused
		label = constants.LABEL_PLAY if is_paused else constants.LABEL_PAUSE
		self.play_button.SetLabel(label)
		self.play_button.SetName(label)
		self.play_button.Enable()
		self.status_text.SetLabel(constants.STATUS_PAUSED if is_paused else constants.STATUS_PLAYING)

	def _playback_finished(self, request_id):
		if request_id != self.playback_request_id:
			return
		self.playback_item_id = None
		self.playback_is_paused = None
		self.play_button.SetLabel(constants.LABEL_PLAY)
		self.play_button.SetName(constants.LABEL_PLAY)
		self.play_button.Enable()
		self.status_text.SetLabel(constants.STATUS_READY)

	def _playback_failed(self, request_id, message):
		if request_id != self.playback_request_id:
			return
		self.playback_item_id = None
		self.playback_is_paused = None
		self.play_button.SetLabel(constants.LABEL_PLAY)
		self.play_button.SetName(constants.LABEL_PLAY)
		self.play_button.Enable()
		self.status_text.SetLabel(message)

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
		self.history_list.delete_item(item)
