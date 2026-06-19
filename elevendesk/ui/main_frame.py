import wx

from elevendesk import config
from elevendesk import constants
from elevendesk import playback
from elevendesk.ui.dialogs.clone_voice_dialog import CloneVoiceDialog
from elevendesk.ui.dialogs.history_dialog import HistoryDialog
from elevendesk.ui.dialogs.pronunciation_dialog import PronunciationDialog
from elevendesk.ui.dialogs.settings_dialog import SettingsDialog
from elevendesk.ui.dialogs.voice_library_dialog import VoiceLibraryDialog
from elevendesk.ui.panels.sfx_panel import SoundEffectsPanel
from elevendesk.ui.panels.stt_panel import SpeechToTextPanel
from elevendesk.ui.panels.tts_panel import TextToSpeechPanel
from elevendesk.ui.panels.voice_design_panel import VoiceDesignPanel


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title=constants.APP_TITLE, size=constants.FRAME_SIZE)
		self.non_modal_dialogs = []
		self._create_menu_bar()
		self.notebook = wx.Notebook(self, name=constants.APP_TITLE)
		self.tts_panel = TextToSpeechPanel(self.notebook)
		self.stt_panel = SpeechToTextPanel(self.notebook)
		self.sfx_panel = SoundEffectsPanel(self.notebook)
		self.voice_design_panel = VoiceDesignPanel(self.notebook, self.tts_panel)
		self.notebook.AddPage(self.tts_panel, constants.TAB_TTS)
		self.notebook.AddPage(self.stt_panel, constants.TAB_STT)
		self.notebook.AddPage(self.sfx_panel, constants.TAB_SFX)
		self.notebook.AddPage(self.voice_design_panel, constants.TAB_VOICE_DESIGN)
		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Centre()

	def initialize(self):
		if not config.load_config()[constants.KEY_API_KEY]:
			preferences_dialog = SettingsDialog(self)
			if preferences_dialog.ShowModal() == wx.ID_OK:
				self.tts_panel._apply_defaults()
				self.tts_panel.refresh_voices()
			preferences_dialog.Destroy()
		self.Show()
		wx.CallAfter(self.tts_panel.focus_text_input)

	def _create_menu_bar(self):
		menu_bar = wx.MenuBar()
		file_menu = wx.Menu()
		self.save_output_item = file_menu.Append(wx.ID_ANY, constants.MENU_SAVE_LAST_OUTPUT)
		self.open_audio_item = file_menu.Append(wx.ID_ANY, constants.MENU_OPEN_AUDIO_FILE)
		file_menu.AppendSeparator()
		self.exit_item = file_menu.Append(wx.ID_EXIT, constants.MENU_EXIT)
		tools_menu = wx.Menu()
		self.voice_library_item = tools_menu.Append(wx.ID_ANY, constants.MENU_VOICE_LIBRARY)
		self.clone_voice_item = tools_menu.Append(wx.ID_ANY, constants.MENU_CLONE_VOICE)
		self.history_item = tools_menu.Append(wx.ID_ANY, constants.MENU_HISTORY)
		self.pronunciation_item = tools_menu.Append(wx.ID_ANY, constants.MENU_PRONUNCIATION)
		settings_menu = wx.Menu()
		self.preferences_item = settings_menu.Append(wx.ID_PREFERENCES, constants.MENU_PREFERENCES)
		help_menu = wx.Menu()
		self.about_item = help_menu.Append(wx.ID_ABOUT, constants.MENU_ABOUT)
		menu_bar.Append(file_menu, constants.MENU_FILE)
		menu_bar.Append(tools_menu, constants.MENU_TOOLS)
		menu_bar.Append(settings_menu, constants.MENU_SETTINGS)
		menu_bar.Append(help_menu, constants.MENU_HELP)
		self.SetMenuBar(menu_bar)
		self.Bind(wx.EVT_MENU, self._on_save_last_output, self.save_output_item)
		self.Bind(wx.EVT_MENU, self._on_open_audio, self.open_audio_item)
		self.Bind(wx.EVT_MENU, self._on_exit, self.exit_item)
		self.Bind(wx.EVT_MENU, self._on_voice_library, self.voice_library_item)
		self.Bind(wx.EVT_MENU, self._on_clone_voice, self.clone_voice_item)
		self.Bind(wx.EVT_MENU, self._on_history, self.history_item)
		self.Bind(wx.EVT_MENU, self._on_pronunciation, self.pronunciation_item)
		self.Bind(wx.EVT_MENU, self._on_preferences, self.preferences_item)
		self.Bind(wx.EVT_MENU, self._on_about, self.about_item)

	def _show_non_modal_dialog(self, dialog):
		self.non_modal_dialogs.append(dialog)
		dialog.Bind(wx.EVT_CLOSE, self._on_non_modal_close)
		dialog.Show()

	def _on_non_modal_close(self, event):
		dialog = event.GetEventObject()
		if dialog in self.non_modal_dialogs:
			self.non_modal_dialogs.remove(dialog)
		dialog.Destroy()

	def _on_save_last_output(self, event):
		current_panel = self.notebook.GetCurrentPage()
		if hasattr(current_panel, constants.METHOD_SAVE_LAST_OUTPUT):
			current_panel.save_last_output(self)
			return
		if hasattr(current_panel, constants.METHOD_GET_LAST_OUTPUT):
			audio_bytes, output_format = current_panel.get_last_output()
			self.save_audio_bytes(audio_bytes, output_format)

	def _on_open_audio(self, event):
		self.notebook.SetSelection(self.notebook.GetPageIndex(self.stt_panel))
		self.stt_panel.open_audio_file()

	def _on_exit(self, event):
		self.Close()

	def _on_voice_library(self, event):
		self._show_non_modal_dialog(VoiceLibraryDialog(self, self.tts_panel))

	def _on_clone_voice(self, event):
		dialog = CloneVoiceDialog(self)
		if dialog.ShowModal() == wx.ID_OK:
			self.tts_panel.refresh_voices()
		dialog.Destroy()

	def _on_history(self, event):
		self._show_non_modal_dialog(HistoryDialog(self))

	def _on_pronunciation(self, event):
		self._show_non_modal_dialog(PronunciationDialog(self))

	def _on_preferences(self, event):
		dialog = SettingsDialog(self)
		if dialog.ShowModal() == wx.ID_OK:
			self.tts_panel._apply_defaults()
			self.tts_panel.refresh_voices()
		dialog.Destroy()

	def _on_about(self, event):
		wx.MessageBox(
			constants.ABOUT_TEXT_TEMPLATE.format(constants.APP_NAME, constants.APP_VERSION),
			constants.TITLE_ABOUT,
			wx.OK | wx.ICON_INFORMATION,
			self,
		)

	def save_audio_bytes(self, audio_bytes, output_format, status_text=None):
		if not audio_bytes:
			return False
		extension, wildcard = constants.OUTPUT_FILE_OPTIONS.get(
			output_format,
			constants.DEFAULT_OUTPUT_FILE_OPTION,
		)
		default_file = constants.DEFAULT_AUDIO_BASENAME + extension
		output_directory = config.load_config()[constants.KEY_OUTPUT_DIRECTORY]
		with wx.FileDialog(
			self,
			message=constants.TITLE_SAVE_AUDIO,
			defaultDir=output_directory,
			defaultFile=default_file,
			wildcard=wildcard,
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return False
			file_path = dialog.GetPath()
		try:
			with open(file_path, constants.FILE_MODE_BINARY_WRITE) as output_file:
				output_file.write(audio_bytes)
		except OSError as error:
			if status_text:
				status_text.SetLabel(str(error))
			else:
				wx.MessageBox(str(error), constants.TITLE_ERROR, wx.OK | wx.ICON_ERROR, self)
			return False
		if status_text:
			status_text.SetLabel(constants.STATUS_SAVED + file_path)
		return True

	def _on_close(self, event):
		for dialog in list(self.non_modal_dialogs):
			dialog.Destroy()
		self.non_modal_dialogs = []
		playback.cleanup()
		event.Skip()
