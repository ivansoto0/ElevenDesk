import sys

import wx


def create_choice(parent, choices=None, name=None, **kwargs):
	if choices is None:
		choices = []
	if sys.platform == 'darwin':
		widget = wx.Choice(parent, choices=choices, **kwargs)
	else:
		kwargs['style'] = kwargs.get('style', 0) | wx.CB_READONLY
		widget = wx.ComboBox(parent, choices=choices, **kwargs)
	if name:
		widget.SetName(name)
	return widget
