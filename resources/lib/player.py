# -*- coding: utf-8 -*-
"""Define a subclass of ``xmbc.Player``"""

from __future__ import absolute_import
try:
    import thread  # python 2
except ImportError:
    import _thread as thread  # python 3
import os
import xbmc
from . import addon
from .utils import create_playlist, log


class Player(xbmc.Player):
    """A child class of ``xbmc.Player``.

    The main features of this class are:
        - To override on ``onPlayBackStopped`` and ``onPlayBackEnded`` callback functions.
        - To start a thread which keeps track of the position of currently playing BGM.

    """
    def __init__(self):
        super(Player, self).__init__()

        self.playlist = self.load_playlist()
        self.BGM_position = -1
        self.BGM_seektime = 0
        self.AVstarted = False

        # Thread automatically ends when main thread does.
        thread.start_new_thread(self.track_BGM, ())
        self.mute(False)

    def mute(self, switch):
        """Mute on/off

        Args:
            switch (bool): Mute on if True, off otherwise.

        """
        state = xbmc.getCondVisibility('Player.Muted')
        if bool(state) != switch:
            xbmc.executebuiltin('Mute()')
        
    def load_playlist(self):
        """Load or create--if necessary--a playlist to play BGM.

        If user chose a playlist in the addon configuration, this function loads the playlist chosen.
        Or, in the case that user chose a directory(folder), this function first looks for
        ``BGM.m3u`` file in your addon profile directory(e.g., /home/[username]/.kodi/userdata/slideshow-BGM/
        on linux; C:\Users\\[username]\\AppData\\Roaming\\Kodi\\userdata\\slideshow-BGM on Windows).
        And if the file exists AND its modification time is newer than settings.xml's in the same directory,
        load that BGM.m3u file; otherwise, it creates ``BGM.m3u`` file in the addon profile directory and load it.

        Returns:
            Playlist object(:obj:`xbmc.PlayList`) if successful, ``None``  otherwise.

        """
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

        if addon.getSetting('type') == 'Playlist':
            playlist_file = addon.getSetting('playlist')
        else:  # If 'Directory'
            playlist_file = os.path.join(xbmc.translatePath(addon.getAddonInfo('profile')),
                                         'BGM.m3u')
            settings_file = os.path.join(xbmc.translatePath(addon.getAddonInfo('profile')),
                                         'settings.xml')
            if os.path.exists(playlist_file) and \
                    os.path.getmtime(playlist_file) > os.path.getmtime(settings_file):
                pass
            else:
                playlist_file = create_playlist(addon.getSetting('directory'))

        playlist.load(playlist_file)
        if addon.getSettingBool('shuffle'):
            playlist.shuffle()
        return playlist

    def play_BGM(self):
        """Play BGM if currently not playing video or audio.

        """
        # Wait till the previous play--if any--ends completely.
        xbmc.sleep(500)
        #: If something--like video slideshow--is playing on till now, do nothing.
        if not self.isPlaying():
            if self.BGM_position == -1:  # first song
                self.play(self.playlist, startpos=self.BGM_position)
            else:
                self.mute(True)  # prevent sound overlap 
                self.play(self.playlist, startpos=self.BGM_position)
                # Wait until play actually begins. Ugly again.
                # Blocking methods such as Event.wait or Lock.acquire will freeze though.
                while not self.AVstarted:
                    xbmc.sleep(100)
                # self.seekTime(self.BGM_seektime) <-- Not Work
                xbmc.executebuiltin('Seek(%s)' % self.BGM_seektime)
                xbmc.sleep(500)
                self.mute(False)

    def track_BGM(self):
        """Keep track of BGM playing.

        """
        while xbmc.getCondVisibility('Slideshow.IsActive'):
            if self.isPlayingAudio():
                position = self.playlist.getposition()
                seektime = self.getTime()
                # Guard condition from kodi's thread intervention.
                if position >= 0 and seektime > 0:
                    self.BGM_position = position
                    self.BGM_seektime = seektime

            xbmc.sleep(1000)

    def onPlayBackStopped(self):
        """Callback function called when audio/video play stops by user.

        """
        self.AVstarted = False
        self.play_BGM()

    def onPlayBackEnded(self):
        """Callback function called when audio/video play ends normally.

        """
        self.AVstarted = False
        self.play_BGM()

    def onAVStarted(self):
        """Callback function called when audio/video has actually started

        """
        self.AVstarted = True
