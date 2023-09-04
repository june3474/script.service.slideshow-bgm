# -*- coding: utf-8 -*-
"""A subclass of :class:`xmbc.Player`"""

import _thread as thread
import os
import xbmc, xbmcvfs
from . import addon
from .utils import create_playlist, log


class Player(xbmc.Player):
    """A subclass of :class:`xbmc.Player`.

    The main features of this class are:
        - To override callback functions like :meth:`onPlayBackStopped` and 
        :meth:`onPlayBackEnded`.
        - To start a thread which keeps track of the position of currently 
          playing background music.
    
    .. Note::

        :class:`Player` seems to be a Singleton.

    """
    def __init__(self):
        super().__init__()

        # Check if the playlist is vaild.
        self.playlist = self.get_playlist_file()
        if not self.playlist:
            raise ValueError('Invalid Playlist.')
        self.playlist_type = os.path.splitext(self.playlist)[1:][0][1:]
        # For playlist of which length is 0 like .xsp or pls with audio stream,
        # playoffset is pointless and ignored(no error).
        self.random = addon.getSettingBool('random') if self.playlist_type == 'm3u' else True
        # After Mute() is called, The value of ``Player.Muted`` does not change
        # immediatly. So we manage the mute state ourselves via ``is_muted``.
        self.is_muted = xbmc.getCondVisibility('Player.Muted')
        self.bgm_position = -1
        self.set_player()

    def set_player(self):
        """Set the properties of randomness and repeat.

        A monkey patch for PlayerControl() that works only after the Player starts.
        
        """
        self.mute(True)
        xbmc.executebuiltin('PlayMedia(%s)' % self.playlist)
        xbmc.executebuiltin('PlayerControl(Play)')  # Actually, Pause.
        if self.random:
            xbmc.executebuiltin('PlayerControl(RandomOn)')
        else:
            xbmc.executebuiltin('PlayerControl(RandomOff)')
        # Set repeat. by default, RepeatAll
        xbmc.executebuiltin('PlayerControl(RepeatAll)')
        xbmc.executebuiltin('PlayerControl(Stop)')
        self.mute(False)

        # Thread will automatically end when main thread does.
        thread.start_new_thread(self.track_bgm, ())

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
        this function first looks for ``bgm.m3u`` file in the addon profile 
        directory.
        FYI, the ``addon profile directory`` is:
            On linux, $HOME/.kodi/userdata/script.slideshow-bgm/;
            On Windows, %AppData%\\Roaming\\Kodi\\userdata\\script.slideshow-bgm

        If ``bgm.m3u`` exists AND its modification time is newer than 
        ``settings.xml``'s in the same directory, return the path of ``bgm.m3u``; 
        otherwise, it creates ``bgm.m3u`` in the ``addon profile directory`` 
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
            with videos, and if any video clips are included in the slideshow, 
            Player might be playing a video when this method starts to run.
            Or, after the callback functions were called, kodi might request 
            to play something before this function actually starts to play BGM.

        """
        # ``xbmc.getCondVisibility('Slideshow.IsVideo')`` is necessary because
        # when the next slideshow item is a video clip and it is on the process
        # of loading--i.e., it's not playing yet--we don't need to play bgm.
        if self.isPlaying() or xbmc.getCondVisibility('Slideshow.IsVideo'):
            # Wait for upto 500ms considering the asynchronousness of infolabels.
            for i in range(5):
                xbmc.sleep(100)
                if not (self.isPlaying() or xbmc.getCondVisibility('Slideshow.IsVideo')):
                    break
                elif i == 4:
                    log('play rejected. title: %s slide: %s' % \
                        (xbmc.getInfoLabel('Player.Title'), xbmc.getInfoLabel('Slideshow.Filename')))
                    return

        log('play started. title: %s slide: %s' % \
            (xbmc.getInfoLabel('Player.Title'), xbmc.getInfoLabel('Slideshow.Filename')))
        
        # We use executebuiltin() because xbmc.Player.play() does not play
        # the smart playlist(.xsp).
        if self.random:
            #self.play(item=self.playlist, startpos=self.bgm_position+1)
            xbmc.executebuiltin('PlayMedia(%s)' % self.playlist)
        else:
            #self.play(item=self.playlist, startpos=self.bgm_position+1)
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

        In particular, this event happens when the user click the '->' button 
        to move on the next item while slideshowing a video clip. 

        """
        self.play_bgm()
        
    def onPlayBackEnded(self):
        """Callback function called when audio/video play ends normally.

        In particular, this event happens when slideshowing a video clip ends.

        """
        self.play_bgm()
        
    def onAVStarted(self):
        """Callback function called when audio/video has actually started.

        Sometimes, e.g., after slideshowing a video clip, slideshow pauses.(issue #7) 

        """       
        if self.isPlayingAudio() and xbmc.getCondVisibility('Slideshow.IsPaused'):
            #json = '{"jsonrpc":"2.0", "method":"%s", "params":%s, "id":1}' \
            #    % ('Input.ButtonEvent', '{"button":"space", "keymap":"KB"}')
            #xbmc.executeJSONRPC(json)
            xbmc.executebuiltin('Action(PlayPause)')