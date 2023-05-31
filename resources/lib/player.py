# -*- coding: utf-8 -*-
"""Define a subclass of ``xmbc.Player``"""

import _thread as thread
import os
import xbmc, xbmcvfs
from . import addon
from .utils import create_playlist, log


class Player(xbmc.Player):
    """A subclass of ``xbmc.Player``.

    The main features of this class are:
        - To override on ``onPlayBackStopped`` and ``onPlayBackEnded`` 
          callback functions.
        - To start a thread which keeps track of the position of currently 
          playing background music.
    By the way, ``Player`` class of ``Kodi`` seems to be a Singleton.

    """
    def __init__(self):
        super().__init__()

        # Check if the playlist is vaild.
        self.playlist = self.get_playlist_file()
        if not self.playlist:
            raise ValueError('Invalid Playlist!')

        # After Mute() is called, 'Player.Muted' is not always correct.
        # Maybe it takes time for the correct value to be set .
        self.is_muted = xbmc.getCondVisibility('Player.Muted')
        self.bgm_position = -1
        self.set_player()

    def set_player(self):
        """Set the properties of randomness and repeat.

        A monkey patch for that PlayerControl() only works after the Player starts.
        
        """
        self.mute(True)
        # Check & Set the randomness of the playlist.
        self.playlist_random = addon.getSettingBool('random')
        xbmc.executebuiltin('PlayMedia(%s)' % self.playlist)
        xbmc.executebuiltin('PlayerControl(Play)')  # Actually, Pause.
        if self.playlist_random:
            xbmc.executebuiltin('PlayerControl(RandomOn)')
        else:
            xbmc.executebuiltin('PlayerControl(RandomOff)')
            # If not random, we keep the track of the offset of the playlist.
            # Thread will automatically end when main thread does.
            thread.start_new_thread(self.track_bgm, ())

        # Set repeat. by default, RepeatAll
        xbmc.executebuiltin('PlayerControl(RepeatAll)')
        xbmc.executebuiltin('PlayerControl(Stop)')
        self.mute(False)

    def mute(self, switch=None):
        """Toggle or set the mute state of the Player
        
        Args:
            switch (None or bool): 
                If ``switch`` is None, toggle the mute state.
                elif ``switch`` is True, mute on.
                else ``switch`` is False, mute off.

        """
        if switch is None or (switch ^ self.is_muted):  # XOR
            xbmc.executebuiltin('Mute')  # 'Mute()' also works
            self.is_muted = not self.is_muted

    def get_playlist_file(self):
        """Get the filepath of the background music playlist.

        If the user choose a playlist in the addon configuration, this function 
        returns the path of the playlist chosen. Or, if user choose a directory, 
        this function first looks for ``bgm.m3u`` file in your addon profile 
        directory.
        FYI the ``addon profile directory`` is:
            On linux, $HOME/.kodi/userdata/script.service.slideshow-bgm/;
            On Windows, %AppData%\\Roaming\\Kodi\\userdata\\script.service.slideshow-bgm

        If ``bgm.m3u`` exists AND its modification time is newer than 
        ``settings.xml``'s in the same directory, return the pahth of ``bgm.m3u``; 
        otherwise, it creates ``bgm.m3u`` in the addon profile directory 
        and returns the path of it.

        Returns:
            str: the path of the playlist if successful, ``None``  otherwise.

        """
        if addon.getSetting('type') == 'Playlist':
            playlist_file = addon.getSetting('playlist')
        else:  # 'Directory'
            profile_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
            playlist_file = os.path.join(profile_dir, 'bgm.m3u')
            settings_file = os.path.join(profile_dir, 'settings.xml')
            playlist_st = xbmcvfs.Stat(playlist_file)
            settings_st = xbmcvfs.Stat(settings_file)
            # We don't use os.path.exists() here due to 'filesystemencoding'
            if xbmcvfs.exists(playlist_file) and \
                    playlist_st.st_mtime() > settings_st.st_mtime():
                pass
            else:
                bgm_dir = addon.getSetting('directory').encode('utf-8')
                playlist_file = create_playlist(bgm_dir)

        return playlist_file

    def play_bgm(self):
        """Play background music if currently not playing video/audio.

        Note:
            When this method is called by onPlayBackStopped()/onPlayBackended(),
            Player might be playing something already.
            For example, If we have selected the option to allow a slideshow 
            with videos, and if there are videos in the list to be included in 
            the slideshow, then Player might be playing a video by the time 
            this function starts to run.
            Or, after the callback functions were called, kodi might request 
            to play something before this function starts.

        """
        if self.isPlaying():
            # Wait for upto 500ms for the previous play to ends completely .
            for i in range(5):
                xbmc.sleep(100)
                if not self.isPlaying():
                    break
                elif i == 4:
                    return
        
        #log('play started. random: %s, bgm_position: %d, title: %s' % \
        #    (self.playlist_random, self.bgm_position, xbmc.getInfoLabel('Player.Title')))
        
        # We use executebuiltin() because xbmc.Player.play() does not play
        # the smart playlist(.xsp).
        if self.playlist_random:
            xbmc.executebuiltin('PlayMedia(%s)' % self.playlist)
        else:
            # For playlist of which length is 0 like .xsp or pls with audio 
            # stream, playoffset is pointless and ignored(no error).
            xbmc.executebuiltin('PlayMedia(%s, playoffset=%d)' % \
                                (self.playlist, self.bgm_position+1))

    def track_bgm(self):
        """Keep track of bgm playing.

        """
        while xbmc.getCondVisibility('Slideshow.IsActive'):
            if self.isPlayingAudio():
                position = int(xbmc.getInfoLabel('Playlist.Position(music)'))
                # Guard condition from kodi's thread intervention.
                if position >= 0:
                    self.bgm_position = position
            xbmc.sleep(1000)

    def onPlayBackStopped(self):
        """Callback function called when audio/video play stops by user.

        """
        self.play_bgm()

    def onPlayBackEnded(self):
        """Callback function called when audio/video play ends normally.

        """
        self.play_bgm()

    def onAVStarted(self):  # Not used currently
        """Callback function called when audio/video has actually started.

        """
        super().onAVStarted()
