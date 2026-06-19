import wx

from elevendesk import constants
from elevendesk.ui.main_frame import MainFrame


class ElevenDeskApp(wx.App):
	def OnInit(self):
		self.SetAppName(constants.APP_NAME)
		main_frame = MainFrame()
		self.SetTopWindow(main_frame)
		main_frame.initialize()
		return True
