# -*- coding: utf-8 -*-
"""Define a subclass of ``xmbc.Player``"""

import _thread as thread
import os
import xbmc, xbmcvfs
from . import addon
from .utils import create_playlist, log


class Player(xbmc.Player):
    """A child class of ``xbmc.Player``.

    The main features of this class are:
        - To override on ``onPlayBackStopped`` and ``onPlayBackEnded`` callback functions.
        - To start a thread which keeps track of the position of currently playing background music.

    """
    def __init__(self):
        super(Player, self).__init__()

        self.playlist = self.load_playlist()
        self.bgm_position = -1
        self.bgm_seektime = 0
        self.AVstarted = False
        self.mute(False)

        # Thread automatically ends when main thread does.
        thread.start_new_thread(self.track_bgm, ())

    @staticmethod
    def mute(switch):
        """Mute on/off.

        Args:
            switch (bool): Mute on if True, off otherwise.

        """
        state = xbmc.getCondVisibility('Player.Muted')
        if bool(state) != switch:
            xbmc.executebuiltin('Mute()')

    @staticmethod
    def load_playlist():
        """Load a playlist of background music.

        When user chose a playlist in the addon configuration, this function loads the playlist chosen.
        In the case that user chose a directory(folder), this function loads ``bgm.m3u`` file in your addon profile
        directory(e.g., /home/[username]/.kodi/userdata/script.service.slideshow-bgm on linux;
        C:\\Users\\[username]\\AppData\\Roaming\\Kodi\\userdata\\script.service.slideshow-bgm on Windows).

        Returns:
            Playlist object(:obj:`xbmc.PlayList`) if successful, ``None``  otherwise.

        """
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

        if addon.getSetting('type') == 'Playlist':
            playlist_file = addon.getSetting('playlist')
        else:  # if 'Directory'
            playlist_file = os.path.join(xbmcvfs.translatePath(addon.getAddonInfo('profile')),
                                         'bgm.m3u')

        playlist.load(playlist_file)
        log('playlist %s loaded' % playlist_file)
        playlist.shuffle(addon.getSettingBool('shuffle'))
        return playlist

    def play_bgm(self):
        """Play background music if currently not playing video or audio.

        """
        # Wait till the previous play--if any--ends completely.
        xbmc.sleep(500)
        #: If something--like video slideshow--is playing on till now, do nothing.
        if not self.isPlaying():
            if self.bgm_position == -1:  # first play
                log('play started')
                self.play(self.playlist, startpos=self.bgm_position)
                xbmc.executebuiltin('PlayerControl(RepeatAll)')
            else:
                self.mute(True)  # prevent sound overlap
                log('play resumed')
                self.play(self.playlist, startpos=self.bgm_position)
                # Wait until play actually begins. Ugly again.
                # Blocking methods such as Event.wait or Lock.acquire will freeze though.
                while not self.AVstarted:
                    xbmc.sleep(100)
                # self.seekTime(self.bgm_seektime) <-- Not Work
                xbmc.executebuiltin('Seek(%s)' % self.bgm_seektime)
                xbmc.sleep(500)
                self.mute(False)
        else:
            log('play ignored: playing something other')

        log('play stopped')

    def track_bgm(self):
        """Keep track of bgm playing.

        """
        while xbmc.getCondVisibility('Slideshow.IsActive'):
            if self.isPlayingAudio():
                position = self.playlist.getposition()
                seektime = self.getTime()
                # Guard condition from kodi's thread intervention.
                if position >= 0 and seektime > 0:
                    self.bgm_position = position
                    self.bgm_seektime = seektime

            xbmc.sleep(1000)

    def onPlayBackStopped(self):
        """Callback function called when audio/video play stops by user.

        """
        self.AVstarted = False
        self.play_bgm()

    def onPlayBackEnded(self):
        """Callback function called when audio/video play ends normally.

        """
        self.AVstarted = False
        self.play_bgm()

    def onAVStarted(self):
        """Callback function called when audio/video has actually started.

        """
        self.AVstarted = True
