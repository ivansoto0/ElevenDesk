import threading

import wx

from elevendesk import api
from elevendesk import config
from elevendesk import constants


class SpeechToTextPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.selected_file_path = constants.EMPTY_TEXT
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._set_tab_order()

	def _create_controls(self):
		self.open_button_label = wx.StaticText(self, label=constants.LABEL_OPEN_AUDIO)
		self.open_button = wx.Button(
			self,
			label=constants.LABEL_OPEN_AUDIO,
			name=constants.NAME_OPEN_TRANSCRIPTION_AUDIO,
		)
		self.selected_file_label = wx.StaticText(self, label=constants.LABEL_SELECTED_FILE)
		self.selected_file = wx.TextCtrl(
			self,
			style=wx.TE_READONLY,
			name=constants.NAME_SELECTED_TRANSCRIPTION_FILE,
		)
		self.transcribe_label = wx.StaticText(self, label=constants.LABEL_TRANSCRIBE)
		self.transcribe_button = wx.Button(
			self,
			label=constants.LABEL_TRANSCRIBE,
			name=constants.NAME_TRANSCRIBE_SELECTED_AUDIO,
		)
		self.transcribe_button.Disable()
		self.transcript_label = wx.StaticText(self, label=constants.LABEL_TRANSCRIPT)
		self.transcript_output = wx.TextCtrl(
			self,
			style=wx.TE_MULTILINE | wx.TE_READONLY,
			name=constants.NAME_TRANSCRIPT_OUTPUT,
		)
		self.copy_label = wx.StaticText(self, label=constants.LABEL_COPY)
		self.copy_button = wx.Button(self, label=constants.LABEL_COPY, name=constants.NAME_COPY_TRANSCRIPT)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE_TRANSCRIPT)
		self.save_button = wx.Button(
			self,
			label=constants.LABEL_SAVE_TRANSCRIPT,
			name=constants.NAME_SAVE_TRANSCRIPT,
		)
		self.copy_button.Disable()
		self.save_button.Disable()
		self.status_text = wx.StaticText(self, label=constants.STATUS_READY, name=constants.LABEL_STATUS)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.open_button_label, self.open_button),
			(self.selected_file_label, self.selected_file),
			(self.transcribe_label, self.transcribe_button),
			(self.transcript_label, self.transcript_output),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			proportion = constants.SIZER_PROPORTION_EXPAND if control is self.transcript_output else constants.SIZER_PROPORTION_NONE
			main_sizer.Add(control, proportion, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer.Add(self.copy_label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
		button_sizer.Add(self.copy_button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.SECTION_GAP)
		button_sizer.Add(self.save_label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
		button_sizer.Add(self.save_button, constants.SIZER_PROPORTION_NONE)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _set_tab_order(self):
		self.selected_file.MoveAfterInTabOrder(self.open_button)
		self.transcribe_button.MoveAfterInTabOrder(self.selected_file)
		self.transcript_output.MoveAfterInTabOrder(self.transcribe_button)
		self.copy_button.MoveAfterInTabOrder(self.transcript_output)
		self.save_button.MoveAfterInTabOrder(self.copy_button)

	def _bind_events(self):
		self.open_button.Bind(wx.EVT_BUTTON, self._on_open)
		self.transcribe_button.Bind(wx.EVT_BUTTON, self._on_transcribe)
		self.copy_button.Bind(wx.EVT_BUTTON, self._on_copy)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)

	def _on_open(self, event):
		self.open_audio_file()

	def open_audio_file(self):
		with wx.FileDialog(
			self,
			message=constants.TITLE_SELECT_AUDIO,
			wildcard=constants.AUDIO_FILE_WILDCARD,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			self.selected_file_path = dialog.GetPath()
		self.selected_file.SetValue(self.selected_file_path)
		self.transcribe_button.Enable()

	def _on_transcribe(self, event):
		if not self.selected_file_path:
			self.status_text.SetLabel(constants.ERROR_AUDIO_REQUIRED)
			return
		self.transcribe_button.Disable()
		self.status_text.SetLabel(constants.STATUS_TRANSCRIBING)
		threading.Thread(target=self._transcribe_worker, daemon=constants.THREAD_DAEMON).start()

	def _transcribe_worker(self):
		try:
			with open(self.selected_file_path, constants.FILE_MODE_BINARY_READ) as audio_file:
				audio_bytes = audio_file.read()
			transcript = api.speech_to_text(audio_bytes, constants.MODEL_SCRIBE_V1)
		except (OSError, api.ElevenDeskAPIError) as error:
			wx.CallAfter(self._transcription_failed, str(error))
			return
		wx.CallAfter(self._transcription_succeeded, transcript)

	def _transcription_succeeded(self, transcript):
		self.transcribe_button.Enable()
		self.transcript_output.SetValue(transcript)
		self.copy_button.Enable(bool(transcript))
		self.save_button.Enable(bool(transcript))
		self.status_text.SetLabel(constants.STATUS_TRANSCRIBED)

	def _transcription_failed(self, message):
		self.transcribe_button.Enable()
		self.status_text.SetLabel(message)

	def _on_copy(self, event):
		if not wx.TheClipboard.Open():
			self.status_text.SetLabel(constants.ERROR_CLIPBOARD)
			return
		try:
			wx.TheClipboard.SetData(wx.TextDataObject(self.transcript_output.GetValue()))
		finally:
			wx.TheClipboard.Close()
		self.status_text.SetLabel(constants.STATUS_COPIED)

	def _on_save(self, event):
		output_directory = config.load_config()[constants.KEY_OUTPUT_DIRECTORY]
		with wx.FileDialog(
			self,
			message=constants.TITLE_SAVE_TRANSCRIPT,
			defaultDir=output_directory,
			defaultFile=constants.DEFAULT_TRANSCRIPT_BASENAME,
			wildcard=constants.TEXT_FILE_WILDCARD,
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			file_path = dialog.GetPath()
		try:
			with open(file_path, constants.FILE_MODE_TEXT_WRITE, encoding=constants.TEXT_ENCODING) as transcript_file:
				transcript_file.write(self.transcript_output.GetValue())
		except OSError as error:
			self.status_text.SetLabel(str(error))
			return
		self.status_text.SetLabel(constants.STATUS_SAVED + file_path)
