import threading

import wx

from elevendesk import config
from elevendesk import constants
from elevendesk import playback
from elevendesk.ui import choices


class AudioDevicesDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_AUDIO_DEVICES, size=constants.SMALL_DIALOG_SIZE)
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		threading.Thread(target=self._load_worker, daemon=constants.THREAD_DAEMON).start()

	def _create_controls(self):
		self.output_label = wx.StaticText(self, label=constants.LABEL_OUTPUT_DEVICE)
		self.output_combo = choices.create_choice(self, name=constants.LABEL_OUTPUT_DEVICE)
		self.input_label = wx.StaticText(self, label=constants.LABEL_INPUT_DEVICE)
		self.input_combo = choices.create_choice(self, name=constants.LABEL_INPUT_DEVICE)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(self, wx.ID_SAVE, constants.LABEL_SAVE, name=constants.LABEL_SAVE)
		self.cancel_label = wx.StaticText(self, label=constants.LABEL_CANCEL)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL, constants.LABEL_CANCEL, name=constants.LABEL_CANCEL)
		self.status_text = wx.StaticText(self, label=constants.STATUS_LOADING, name=constants.LABEL_STATUS)
		self.save_button.Disable()

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.output_label, self.output_combo),
			(self.input_label, self.input_combo),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			main_sizer.Add(control, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer.AddStretchSpacer()
		for label, button in (
			(self.save_label, self.save_button),
			(self.cancel_label, self.cancel_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.CONTROL_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		main_sizer.Add(self.status_text, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _bind_events(self):
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)

	def _load_worker(self):
		try:
			output_devices, input_devices = playback.get_devices()
		except Exception as error:
			wx.CallAfter(self.status_text.SetLabel, str(error))
			return
		wx.CallAfter(self._populate_devices, output_devices, input_devices)

	def _populate_devices(self, output_devices, input_devices):
		settings = config.load_config()
		self._populate_combo(self.output_combo, output_devices, settings[constants.KEY_OUTPUT_DEVICE])
		self._populate_combo(self.input_combo, input_devices, settings[constants.KEY_INPUT_DEVICE])
		self.save_button.Enable()
		self.status_text.SetLabel(constants.STATUS_READY)

	def _populate_combo(self, combo, devices, saved_value):
		for device in devices:
			combo.Append(device)
		if saved_value:
			selection = combo.FindString(saved_value)
			if selection != wx.NOT_FOUND:
				combo.SetSelection(selection)
				return
		if combo.GetCount():
			combo.SetSelection(constants.FIRST_ITEM_INDEX)

	def _on_save(self, event):
		settings = config.load_config()
		output_selection = self.output_combo.GetStringSelection()
		input_selection = self.input_combo.GetStringSelection()
		settings[constants.KEY_OUTPUT_DEVICE] = output_selection if output_selection != constants.LABEL_DEFAULT_DEVICE else constants.EMPTY_TEXT
		settings[constants.KEY_INPUT_DEVICE] = input_selection if input_selection != constants.LABEL_DEFAULT_DEVICE else constants.EMPTY_TEXT
		try:
			config.save_config(settings)
		except OSError as error:
			wx.MessageBox(str(error), constants.TITLE_ERROR, wx.OK | wx.ICON_ERROR, self)
			return
		playback.reset_output()
		self.EndModal(wx.ID_OK)
