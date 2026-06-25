import sys
import traceback
from pathlib import Path

import wx

from elevendesk.app import ElevenDeskApp
from elevendesk import constants


_LOG_PATH = Path.home() / "Documents" / "elevendesk_errors.log"


def _log(tb):
	with open(_LOG_PATH, "a", encoding=constants.TEXT_ENCODING) as f:
		f.write(tb)


def _show_error(tb):
	_log(tb)
	try:
		if not wx.GetApp():
			wx.App(False)
		dlg = wx.Dialog(None, title=constants.TITLE_ERROR, size=(640, 420))
		sizer = wx.BoxSizer(wx.VERTICAL)
		text = wx.TextCtrl(dlg, value=tb, style=wx.TE_MULTILINE | wx.TE_READONLY, name="Traceback")
		sizer.Add(text, 1, wx.EXPAND | wx.ALL, constants.PANEL_BORDER)
		note = wx.StaticText(dlg, label="Error log: " + str(_LOG_PATH))
		sizer.Add(note, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, constants.PANEL_BORDER)
		btn = wx.Button(dlg, wx.ID_OK, label=constants.LABEL_CLOSE)
		sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, constants.PANEL_BORDER)
		dlg.SetSizer(sizer)
		dlg.ShowModal()
		dlg.Destroy()
	except Exception:
		pass


def main():
	application = ElevenDeskApp(False)
	application.MainLoop()


def run():
	try:
		main()
	except Exception:
		_show_error(traceback.format_exc())
		sys.exit(1)


if __name__ == constants.MAIN_MODULE_NAME:
	run()
