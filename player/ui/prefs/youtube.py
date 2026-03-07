import wx
from gettext import gettext as _

from config.constants import YT_DLP_UPDATE_CHANNELS


class YouTubeSettingsPanel(wx.Panel):
    def __init__(self, parent, settings, on_download_components=None):
        super().__init__(parent)
        self._settings = settings
        self._on_download_components = on_download_components

        self._audio_only = wx.CheckBox(self, label=_("Play videos as audio only"))
        self._audio_only.SetValue(self._settings.get_yt_audio_only())

        self._quality_label = wx.StaticText(self, label=_("Video quality"))
        self._quality_labels = [_("Low"), _("Medium"), _("Best")]
        self._quality_values = ["low", "medium", "best"]
        self._quality_choice = wx.Choice(self, choices=self._quality_labels)
        self._set_quality_selection(self._settings.get_yt_video_quality())

        self._mixed_label = wx.StaticText(
            self, label=_("Video+playlist link behavior")
        )
        self._mixed_labels = [
            _("Ask every time"),
            _("Play the video"),
            _("Open the playlist"),
        ]
        self._mixed_values = ["ask", "video", "playlist"]
        self._mixed_choice = wx.Choice(self, choices=self._mixed_labels)
        self._set_mixed_selection(self._settings.get_yt_mixed_link_mode())

        self._channel_label = wx.StaticText(self, label=_("yt-dlp update channel"))
        self._channel_values = list(YT_DLP_UPDATE_CHANNELS)
        self._channel_labels = [text.title() for text in self._channel_values]
        self._channel_choice = wx.Choice(self, choices=self._channel_labels)
        self._set_channel_selection(self._settings.get_yt_dlp_channel())
        self._check_updates_startup = wx.CheckBox(
            self,
            label=_("Check for yt-dlp updates on startup"),
        )
        self._check_updates_startup.SetValue(
            self._settings.get_check_yt_updates_startup()
        )
        self._download_button = wx.Button(self, label=_("Download YouTube components"))
        self._download_button.Bind(wx.EVT_BUTTON, self._on_download)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._audio_only, 0, wx.ALL, 8)

        quality_sizer = wx.BoxSizer(wx.VERTICAL)
        quality_sizer.Add(self._quality_label, 0, wx.BOTTOM, 4)
        quality_sizer.Add(self._quality_choice, 0, wx.EXPAND)
        sizer.Add(quality_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        mixed_sizer = wx.BoxSizer(wx.VERTICAL)
        mixed_sizer.Add(self._mixed_label, 0, wx.BOTTOM, 4)
        mixed_sizer.Add(self._mixed_choice, 0, wx.EXPAND)
        sizer.Add(mixed_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        channel_sizer = wx.BoxSizer(wx.VERTICAL)
        channel_sizer.Add(self._channel_label, 0, wx.BOTTOM, 4)
        channel_sizer.Add(self._channel_choice, 0, wx.EXPAND)
        sizer.Add(channel_sizer, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)
        sizer.Add(
            self._check_updates_startup,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM,
            8,
        )
        sizer.Add(self._download_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        self.SetSizer(sizer)

    def apply(self):
        self._settings.set_yt_audio_only(self._audio_only.GetValue())

        qidx = self._quality_choice.GetSelection()
        if qidx == wx.NOT_FOUND:
            qidx = 1
        self._settings.set_yt_video_quality(self._quality_values[qidx])

        midx = self._mixed_choice.GetSelection()
        if midx == wx.NOT_FOUND:
            midx = 0
        self._settings.set_yt_mixed_link_mode(self._mixed_values[midx])

        cidx = self._channel_choice.GetSelection()
        if cidx == wx.NOT_FOUND:
            cidx = 0
        self._settings.set_yt_dlp_channel(self._channel_values[cidx])
        self._settings.set_check_yt_updates_startup(
            self._check_updates_startup.GetValue()
        )

    def refresh_from_settings(self):
        self._audio_only.SetValue(self._settings.get_yt_audio_only())
        self._set_quality_selection(self._settings.get_yt_video_quality())
        self._set_mixed_selection(self._settings.get_yt_mixed_link_mode())
        self._set_channel_selection(self._settings.get_yt_dlp_channel())
        self._check_updates_startup.SetValue(
            self._settings.get_check_yt_updates_startup()
        )

    def get_context_help(self, focused):
        control = focused
        while control is not None:
            if control is self._audio_only:
                return _(
                    "Play videos as audio only. When enabled, YouTube playback prefers audio streams."
                )
            if control is self._quality_choice:
                return _(
                    "Video quality used when audio-only playback is disabled. "
                    "Low prefers smaller streams, Medium is balanced, Best prefers highest quality."
                )
            if control is self._mixed_choice:
                return _(
                    "Behavior for YouTube links that include both a video ID and a playlist ID. "
                    "Ask every time shows a chooser dialog. "
                    "Play the video opens only the selected video. "
                    "Open the playlist opens the full playlist."
                )
            if control is self._channel_choice:
                return _(
                    "yt-dlp update channel. Stable is recommended. "
                    "Nightly and Master can include newer but less-tested builds."
                )
            if control is self._check_updates_startup:
                return _(
                    "Check for yt-dlp updates on startup. "
                    "When enabled, the app checks local and latest channel versions at launch "
                    "and prompts you to run the standard yt-dlp update when a newer version is available."
                )
            if control is self._download_button:
                return _(
                    "Download YouTube components installs missing YouTube libraries "
                    "such as yt-dlp and Deno."
                )
            if control is self:
                break
            control = control.GetParent()
        return _(
            "YouTube settings page. Configure playback mode, quality, mixed-link behavior, yt-dlp update channel, and startup update checks."
        )

    def _set_quality_selection(self, value):
        try:
            idx = self._quality_values.index(str(value or "medium"))
        except ValueError:
            idx = 1
        self._quality_choice.SetSelection(idx)

    def _set_mixed_selection(self, value):
        try:
            idx = self._mixed_values.index(str(value or "ask"))
        except ValueError:
            idx = 0
        self._mixed_choice.SetSelection(idx)

    def _set_channel_selection(self, channel):
        try:
            idx = self._channel_values.index(str(channel or "").lower())
        except ValueError:
            idx = 0
        self._channel_choice.SetSelection(idx)

    def _on_download(self, _event):
        cidx = self._channel_choice.GetSelection()
        if cidx == wx.NOT_FOUND:
            cidx = 0
        channel = self._channel_values[cidx]
        if self._on_download_components is not None:
            self._on_download_components(self, channel)
