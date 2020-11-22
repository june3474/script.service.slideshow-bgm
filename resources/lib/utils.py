# -*- coding: utf-8 -*-
"""Helper functions"""

from __future__ import absolute_import
import os
import xbmc, xbmcgui
from . import addon


def log(msg):
    """Wrapper function for ``xbmcgui.log()``.

    Args:
        msg (str): message to log.

    """
    xbmc.log('[slideshow-BGM] ' + msg, xbmc.LOGINFO)


def notify(message, icon=xbmcgui.NOTIFICATION_INFO, time=7000, sound=True):
    """Wrapper function of ``xbmcgui.Dialog().notification``.

    Args:
        message (str): message to show.
        icon (str): icon. (default ``xbmcgui.NOTIFICATION_INFO``).
            Other built-in icons:
                - xbmcgui.NOTIFICATION_INFO
                - xbmcgui.NOTIFICATION_WARNING
                - xbmcgui.NOTIFICATION_ERROR
        time (int): time in milliseconds to show.
        sound (bool): whether to play notification sound. (default True)

    """
    header = '[Slideshow-BGM]'
    xbmcgui.Dialog().notification(header, message, icon, time, sound)


def create_playlist(BGM_dir):
    """Create a playlist file(m3u file) with the songs in ``BGM_dir``.

    Args:
        BGM_dir (str): Directory where to look for music files.

    Returns:
        str: The path of newly created playlist file if successful, ``None`` otherwise
        .. Warning::
            If there is no music file in the ``BGM_dir``, this function returns an empty playlist.

    """
    playlist_dir = xbmc.translatePath(addon.getAddonInfo('profile'))
    playlist_file = os.path.join(playlist_dir, 'BGM.m3u')
    music_file_exts = ('.mp2', '.mp3', '.wav', '.ogg', '.wma')

    count = 0
    try:
        with open(playlist_file, 'w') as f:
            f.write('#EXTM3U' + os.linesep * 2)
            for root, dirs, files in os.walk(BGM_dir, followlinks=True):
                for filename in files:
                    if filename.lower().endswith(music_file_exts):
                        f.write(os.path.join(root, filename) + os.linesep)
                        count += 1
    except (IOError,):
        notify("Failed to create a playlist file in "
               + xbmc.translatePath(addon.getAddonInfo('profile')),
               xbmcgui.NOTIFICATION_ERROR)
        return None

    if not count:
        notify('No music file in %s' % BGM_dir,
               xbmcgui.NOTIFICATION_WARNING)

    return playlist_file


def check_config():
    """Check addon settings to see if they are configured properly.

    Returns:
        bool: True if no problem found, False otherwise.

    """
    _type = addon.getSetting('type')
    playlist = addon.getSetting('playlist')
    directory = addon.getSetting('directory')

    if (_type == 'Playlist' and playlist == 'Not Selected') or \
            (_type == 'Directory' and directory == 'Not Selected'):
        notify("You have not yet configured addon settings.",
               xbmcgui.NOTIFICATION_ERROR)
        return False

    if _type == 'Playlist' and not os.path.exists(playlist):
        notify("No such file: %s\n" % playlist + "Check your configuration.",
               xbmcgui.NOTIFICATION_ERROR)
        return False

    if _type == 'Directory' and not os.path.exists(directory):
        notify("No such directory: %s\n" % directory + "Check your configuration.",
               xbmcgui.NOTIFICATION_ERROR)
        return False

    return True
