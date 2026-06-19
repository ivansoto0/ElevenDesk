import os
import threading

import wx
import soundobj

from elevendesk import api
from elevendesk import constants
from elevendesk import playback


class CloneVoiceDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_CLONE_VOICE, size=constants.DIALOG_SIZE)
		self.audio_files = []
		self.is_cloning = False
		self.name_label = wx.StaticText(self, label=constants.LABEL_VOICE_NAME)
		self.name_input = wx.TextCtrl(self, name=constants.LABEL_VOICE_NAME)
		self.description_label = wx.StaticText(self, label=constants.COLUMN_DESCRIPTION)
		self.description_input = wx.TextCtrl(self, name=constants.COLUMN_DESCRIPTION)
		self.files_label = wx.StaticText(self, label=constants.LABEL_AUDIO_FILES)
		self.files_list = wx.ListCtrl(
			self,
			style=wx.LC_REPORT | wx.LC_SINGLE_SEL,
			name=constants.LABEL_AUDIO_FILES,
		)
		for column_index, column_header, column_width in (
			(constants.COLUMN_INDEX_FILE, constants.COLUMN_FILE, constants.COLUMN_WIDTH_FILE),
			(constants.COLUMN_INDEX_DURATION, constants.COLUMN_DURATION, constants.COLUMN_WIDTH_DURATION),
			(constants.COLUMN_INDEX_FORMAT, constants.COLUMN_FORMAT, constants.COLUMN_WIDTH_FORMAT),
			(constants.COLUMN_INDEX_SAMPLE_RATE, constants.COLUMN_SAMPLE_RATE, constants.COLUMN_WIDTH_SAMPLE_RATE),
			(constants.COLUMN_INDEX_CHANNELS, constants.COLUMN_CHANNELS, constants.COLUMN_WIDTH_CHANNELS),
			(constants.COLUMN_INDEX_SIZE, constants.COLUMN_SIZE, constants.COLUMN_WIDTH_SIZE),
			(constants.COLUMN_INDEX_PATH, constants.COLUMN_PATH, constants.COLUMN_WIDTH_PATH),
		):
			self.files_list.InsertColumn(column_index, column_header, width=column_width)
		self.add_label = wx.StaticText(self, label=constants.LABEL_ADD_FILE)
		self.add_button = wx.Button(self, label=constants.LABEL_ADD_FILE, name=constants.LABEL_ADD_FILE)
		self.add_directory_label = wx.StaticText(self, label=constants.LABEL_ADD_DIRECTORY)
		self.add_directory_button = wx.Button(
			self,
			label=constants.LABEL_ADD_DIRECTORY,
			name=constants.LABEL_ADD_DIRECTORY,
		)
		self.remove_label = wx.StaticText(self, label=constants.LABEL_REMOVE_FILE)
		self.remove_button = wx.Button(self, label=constants.LABEL_REMOVE_FILE, name=constants.LABEL_REMOVE_FILE)
		self.rights_checkbox = wx.CheckBox(
			self,
			label=constants.LABEL_VOICE_RIGHTS_CONFIRMATION,
			name=constants.LABEL_VOICE_RIGHTS_CONFIRMATION,
		)
		self.clone_label = wx.StaticText(self, label=constants.LABEL_CLONE)
		self.clone_button = wx.Button(self, label=constants.LABEL_CLONE, name=constants.LABEL_CLONE)
		self.clone_button.Disable()
		self.progress_label = wx.StaticText(self, label=constants.LABEL_CLONE_PROGRESS)
		self.progress_gauge = wx.Gauge(
			self,
			range=constants.PROGRESS_RANGE,
			name=constants.LABEL_CLONE_PROGRESS,
		)
		self.progress_gauge.Hide()
		self.progress_label.Hide()
		self.status_text = wx.StaticText(self, label=constants.STATUS_READY, name=constants.LABEL_STATUS)
		self.progress_timer = wx.Timer(self)
		self._layout_controls()
		self.add_button.Bind(wx.EVT_BUTTON, self._on_add)
		self.add_directory_button.Bind(wx.EVT_BUTTON, self._on_add_directory)
		self.remove_button.Bind(wx.EVT_BUTTON, self._on_remove)
		self.rights_checkbox.Bind(wx.EVT_CHECKBOX, self._on_rights_changed)
		self.clone_button.Bind(wx.EVT_BUTTON, self._on_clone)
		self.Bind(wx.EVT_TIMER, self._on_progress_timer, self.progress_timer)
		self.Bind(wx.EVT_CLOSE, self._on_close)
		self._set_tab_order()

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.name_label, self.name_input),
			(self.description_label, self.description_input),
			(self.files_label, self.files_list),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.files_list else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		for label, button in (
			(self.add_label, self.add_button),
			(self.add_directory_label, self.add_directory_button),
			(self.remove_label, self.remove_button),
			(self.clone_label, self.clone_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.rights_checkbox, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.progress_label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
		main_sizer.Add(self.progress_gauge, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _set_tab_order(self):
		self.description_input.MoveAfterInTabOrder(self.name_input)
		self.files_list.MoveAfterInTabOrder(self.description_input)
		self.add_button.MoveAfterInTabOrder(self.files_list)
		self.add_directory_button.MoveAfterInTabOrder(self.add_button)
		self.remove_button.MoveAfterInTabOrder(self.add_directory_button)
		self.rights_checkbox.MoveAfterInTabOrder(self.remove_button)
		self.clone_button.MoveAfterInTabOrder(self.rights_checkbox)

	def _on_add(self, event):
		with wx.FileDialog(
			self,
			message=constants.TITLE_SELECT_AUDIO,
			wildcard=constants.AUDIO_FILE_WILDCARD,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
		) as dialog:
			if dialog.ShowModal() == wx.ID_OK:
				self._add_audio_files(dialog.GetPaths())

	def _on_add_directory(self, event):
		with wx.DirDialog(
			self,
			message=constants.TITLE_SELECT_AUDIO_DIRECTORY,
			style=wx.DD_DIR_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			directory_path = dialog.GetPath()
		file_paths = []
		for current_directory, directory_names, file_names in os.walk(directory_path):
			directory_names.sort()
			for file_name in sorted(file_names):
				file_path = os.path.join(current_directory, file_name)
				if os.path.splitext(file_name)[constants.INDEX_STEP].lower() in constants.AUDIO_FILE_EXTENSIONS:
					file_paths.append(file_path)
		self._add_audio_files(file_paths)

	def _add_audio_files(self, file_paths):
		added_count = constants.FIRST_ITEM_INDEX
		skipped_count = constants.FIRST_ITEM_INDEX
		limit_count = constants.FIRST_ITEM_INDEX
		existing_paths = {item[constants.KEY_FILE_PATH] for item in self.audio_files}
		for file_path in file_paths:
			normalized_path = os.path.normcase(os.path.abspath(file_path))
			if normalized_path in existing_paths:
				continue
			if len(self.audio_files) >= constants.CLONE_MAX_AUDIO_FILES:
				limit_count += constants.INDEX_STEP
				continue
			try:
				metadata = playback.get_audio_file_metadata(file_path)
			except (soundobj.MiniAudioError, OSError, RuntimeError, ValueError):
				skipped_count += constants.INDEX_STEP
				continue
			metadata[constants.KEY_FILE_PATH] = normalized_path
			self.audio_files.append(metadata)
			existing_paths.add(normalized_path)
			self._append_audio_file(metadata)
			added_count += constants.INDEX_STEP
		if limit_count:
			status_message = constants.STATUS_AUDIO_FILES_LIMIT_TEMPLATE.format(
				added_count,
				skipped_count,
				limit_count,
				constants.CLONE_MAX_AUDIO_FILES,
			)
		else:
			status_message = constants.STATUS_AUDIO_FILES_ADDED_TEMPLATE.format(
				added_count,
				skipped_count,
			)
		self.status_text.SetLabel(status_message)
		self._update_clone_button()

	def _append_audio_file(self, metadata):
		row = self.files_list.InsertItem(
			self.files_list.GetItemCount(),
			metadata[constants.KEY_FILE_NAME],
		)
		self.files_list.SetItem(
			row,
			constants.COLUMN_INDEX_DURATION,
			constants.FILE_DURATION_TEMPLATE.format(metadata[constants.KEY_FILE_DURATION]),
		)
		self.files_list.SetItem(row, constants.COLUMN_INDEX_FORMAT, metadata[constants.KEY_FILE_FORMAT])
		self.files_list.SetItem(
			row,
			constants.COLUMN_INDEX_SAMPLE_RATE,
			constants.FILE_SAMPLE_RATE_TEMPLATE.format(metadata[constants.KEY_FILE_SAMPLE_RATE]),
		)
		self.files_list.SetItem(
			row,
			constants.COLUMN_INDEX_CHANNELS,
			str(metadata[constants.KEY_FILE_CHANNELS]),
		)
		self.files_list.SetItem(
			row,
			constants.COLUMN_INDEX_SIZE,
			constants.FILE_SIZE_TEMPLATE.format(
				metadata[constants.KEY_FILE_SIZE] / constants.BYTES_PER_MEGABYTE
			),
		)
		self.files_list.SetItem(row, constants.COLUMN_INDEX_PATH, metadata[constants.KEY_FILE_PATH])

	def _on_remove(self, event):
		selection = self.files_list.GetFirstSelected()
		if selection != wx.NOT_FOUND:
			del self.audio_files[selection]
			self.files_list.DeleteItem(selection)
			self._update_clone_button()

	def _on_rights_changed(self, event):
		self._update_clone_button()

	def _update_clone_button(self):
		has_valid_file_count = (
			bool(self.audio_files)
			and len(self.audio_files) <= constants.CLONE_MAX_AUDIO_FILES
		)
		self.clone_button.Enable(has_valid_file_count and self.rights_checkbox.IsChecked())

	def _on_clone(self, event):
		name = self.name_input.GetValue().strip()
		if not name:
			self.status_text.SetLabel(constants.ERROR_VOICE_NAME_REQUIRED)
			return
		if not self.audio_files:
			self.status_text.SetLabel(constants.ERROR_CLONE_FILES_REQUIRED)
			return
		if len(self.audio_files) > constants.CLONE_MAX_AUDIO_FILES:
			self.status_text.SetLabel(
				constants.ERROR_CLONE_FILE_LIMIT_TEMPLATE.format(constants.CLONE_MAX_AUDIO_FILES)
			)
			return
		if not self.rights_checkbox.IsChecked():
			self.status_text.SetLabel(constants.ERROR_VOICE_RIGHTS_REQUIRED)
			return
		file_paths = [item[constants.KEY_FILE_PATH] for item in self.audio_files]
		self._set_cloning_state(True)
		self.status_text.SetLabel(constants.STATUS_CLONING_FILES_TEMPLATE.format(len(file_paths)))
		threading.Thread(
			target=self._clone_worker,
			args=(name, self.description_input.GetValue().strip(), file_paths),
			daemon=constants.THREAD_DAEMON,
		).start()

	def _set_cloning_state(self, is_cloning):
		self.is_cloning = is_cloning
		for control in (
			self.name_input,
			self.description_input,
			self.files_list,
			self.add_button,
			self.add_directory_button,
			self.remove_button,
			self.rights_checkbox,
		):
			control.Enable(not is_cloning)
		if is_cloning:
			self.clone_button.Disable()
			self.progress_gauge.SetValue(constants.FIRST_ITEM_INDEX)
			self.progress_label.Show()
			self.progress_gauge.Show()
			self.progress_timer.Start(constants.PROGRESS_PULSE_INTERVAL_MS)
		else:
			self.progress_timer.Stop()
			self.progress_label.Hide()
			self.progress_gauge.Hide()
			self._update_clone_button()
		self.Layout()

	def _on_progress_timer(self, event):
		self.progress_gauge.Pulse()

	def _on_close(self, event):
		if self.is_cloning:
			self.status_text.SetLabel(constants.STATUS_CLONE_CLOSE_BLOCKED)
			event.Veto()
			return
		event.Skip()

	def _clone_worker(self, name, description, file_paths):
		try:
			voice = api.clone_voice(name, description, file_paths)
		except (OSError, api.ElevenDeskAPIError) as error:
			wx.CallAfter(self._clone_failed, str(error))
			return
		wx.CallAfter(self._clone_succeeded, voice)

	def _clone_succeeded(self, voice):
		self.is_cloning = False
		self.progress_timer.Stop()
		self.progress_gauge.SetValue(constants.PROGRESS_COMPLETE)
		self.status_text.SetLabel(constants.STATUS_CLONE_COMPLETE)
		wx.MessageBox(
			constants.SUCCESS_CLONE_TEMPLATE.format(voice[constants.KEY_VOICE_ID]),
			constants.TITLE_SUCCESS,
			wx.OK | wx.ICON_INFORMATION,
			self,
		)
		self.EndModal(wx.ID_OK)

	def _clone_failed(self, message):
		self._set_cloning_state(False)
		self.status_text.SetLabel(message)
