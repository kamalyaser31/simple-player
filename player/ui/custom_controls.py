import wx


class CustomButton(wx.Button):
    def __init__(self, *args, **kwargs):
        wx.Button.__init__(self, *args, **kwargs)

    def AcceptsFocus(self):
        return False

    def AcceptsFocusFromKeyboard(self):
        return False
