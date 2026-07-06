import wx
import traceback


class MainFrameEventsMixin:
    def _on_menu_action(self, event):
        action_id = self._menu_action_map.get(event.GetId())
        if action_id:
            self._controller.handle_action(action_id)
        else:
            event.Skip()

    def _on_exit(self, _event):
        self.Close()

    def _on_close(self, _event):
        try:
            self._controller.shutdown()
        except Exception:
            traceback.print_exc()
        self.Destroy()

    def _on_accelerator(self, event):
        action_id = self._action_id_map.get(event.GetId())
        if action_id:
            self._controller.handle_action(action_id)
        else:
            event.Skip()

    def _on_jump_menu(self, event):
        action_id = self._jump_menu_map.get(event.GetId())
        if action_id:
            self._controller.handle_action(action_id)
        else:
            event.Skip()

    def _on_seek_step_menu(self, event):
        action_id = self._seek_step_menu_map.get(event.GetId())
        if action_id:
            self._controller.handle_action(action_id)
        else:
            event.Skip()

    def _on_char_hook(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE and event.GetModifiers() == wx.MOD_NONE:
            if self._controller.handle_escape():
                return
        event.Skip()
