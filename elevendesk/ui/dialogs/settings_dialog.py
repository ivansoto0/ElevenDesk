import os

import wx

from elevendesk import api
from elevendesk import config
from elevendesk import constants


class SettingsDialog(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, title=constants.TITLE_PREFERENCES, size=constants.SMALL_DIALOG_SIZE)
		self.saved = False
		self.settings = config.load_config()
		self._create_controls()
		self._layout_controls()
		self._bind_events()
		self._load_settings()

	def _create_controls(self):
		self.api_key_label = wx.StaticText(self, label=constants.LABEL_API_KEY)
		self.api_key_input = wx.TextCtrl(self, style=wx.TE_PASSWORD, name=constants.LABEL_API_KEY)
		self.model_label = wx.StaticText(self, label=constants.LABEL_DEFAULT_MODEL)
		self.model_combo = wx.ComboBox(
			self,
			choices=list(constants.MODEL_IDS),
			style=wx.CB_READONLY,
			name=constants.LABEL_DEFAULT_MODEL,
		)
		self.voice_id_label = wx.StaticText(self, label=constants.LABEL_DEFAULT_VOICE_ID)
		self.voice_id_input = wx.TextCtrl(self, name=constants.LABEL_DEFAULT_VOICE_ID)
		self.format_label = wx.StaticText(self, label=constants.LABEL_DEFAULT_OUTPUT_FORMAT)
		self.format_combo = wx.ComboBox(
			self,
			choices=list(constants.OUTPUT_FORMATS),
			style=wx.CB_READONLY,
			name=constants.LABEL_DEFAULT_OUTPUT_FORMAT,
		)
		self.output_directory_label = wx.StaticText(self, label=constants.LABEL_OUTPUT_DIRECTORY)
		self.output_directory_input = wx.TextCtrl(self, name=constants.LABEL_OUTPUT_DIRECTORY)
		self.browse_label = wx.StaticText(self, label=constants.LABEL_BROWSE)
		self.browse_button = wx.Button(self, label=constants.LABEL_BROWSE, name=constants.LABEL_BROWSE)
		self.save_label = wx.StaticText(self, label=constants.LABEL_SAVE)
		self.save_button = wx.Button(self, wx.ID_SAVE, constants.LABEL_SAVE, name=constants.LABEL_SAVE)
		self.cancel_label = wx.StaticText(self, label=constants.LABEL_CANCEL)
		self.cancel_button = wx.Button(self, wx.ID_CANCEL, constants.LABEL_CANCEL, name=constants.LABEL_CANCEL)

	def _layout_controls(self):
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		for label, control in (
			(self.api_key_label, self.api_key_input),
			(self.model_label, self.model_combo),
			(self.voice_id_label, self.voice_id_input),
			(self.format_label, self.format_combo),
			(self.output_directory_label, self.output_directory_input),
		):
			main_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.CONTROL_GAP)
			main_sizer.Add(control, constants.SIZER_PROPORTION_NONE, wx.EXPAND | wx.BOTTOM, constants.SECTION_GAP)
		browse_sizer = wx.BoxSizer(wx.HORIZONTAL)
		browse_sizer.Add(self.browse_label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
		browse_sizer.Add(self.browse_button, constants.SIZER_PROPORTION_NONE)
		main_sizer.Add(browse_sizer, constants.SIZER_PROPORTION_NONE, wx.BOTTOM, constants.SECTION_GAP)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer.AddStretchSpacer()
		for label, button in (
			(self.save_label, self.save_button),
			(self.cancel_label, self.cancel_button),
		):
			button_sizer.Add(label, constants.SIZER_PROPORTION_NONE, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, constants.CONTROL_GAP)
			button_sizer.Add(button, constants.SIZER_PROPORTION_NONE, wx.RIGHT, constants.CONTROL_GAP)
		main_sizer.Add(button_sizer, constants.SIZER_PROPORTION_NONE, wx.EXPAND)
		self.SetSizer(main_sizer)

	def _bind_events(self):
		self.browse_button.Bind(wx.EVT_BUTTON, self._on_browse)
		self.save_button.Bind(wx.EVT_BUTTON, self._on_save)

	def _load_settings(self):
		self.api_key_input.SetValue(self.settings[constants.KEY_API_KEY])
		self.voice_id_input.SetValue(self.settings[constants.KEY_DEFAULT_VOICE_ID])
		self.output_directory_input.SetValue(self.settings[constants.KEY_OUTPUT_DIRECTORY])
		self._select_combo(self.model_combo, self.settings[constants.KEY_DEFAULT_MODEL])
		self._select_combo(self.format_combo, self.settings[constants.KEY_DEFAULT_OUTPUT_FORMAT])

	def _select_combo(self, combo, value):
		selection = combo.FindString(value)
		if selection == wx.NOT_FOUND:
			selection = constants.FIRST_ITEM_INDEX
		combo.SetSelection(selection)

	def _on_browse(self, event):
		with wx.DirDialog(
			self,
			message=constants.TITLE_SELECT_OUTPUT_DIRECTORY,
			defaultPath=self.output_directory_input.GetValue(),
		) as dialog:
			if dialog.ShowModal() == wx.ID_OK:
				self.output_directory_input.SetValue(dialog.GetPath())

	def _on_save(self, event):
		output_directory = self.output_directory_input.GetValue().strip()
		if output_directory:
			os.makedirs(output_directory, exist_ok=True)
		settings = {
			constants.KEY_API_KEY: self.api_key_input.GetValue().strip(),
			constants.KEY_DEFAULT_MODEL: self.model_combo.GetStringSelection(),
			constants.KEY_DEFAULT_VOICE_ID: self.voice_id_input.GetValue().strip(),
			constants.KEY_DEFAULT_OUTPUT_FORMAT: self.format_combo.GetStringSelection(),
			constants.KEY_OUTPUT_DIRECTORY: output_directory,
		}
		try:
			config.save_config(settings)
		except OSError as error:
			wx.MessageBox(str(error), constants.TITLE_ERROR, wx.OK | wx.ICON_ERROR, self)
			return
		api.reset_client()
		self.saved = True
		self.EndModal(wx.ID_OK)
