# -*- coding: utf-8 -*-
"""Helper functions"""

import os
import xbmc, xbmcgui, xbmcvfs
from . import addon


def log(msg):
    """Wrapper function for ``xbmcgui.log()``.

    Args:
        msg (str): message to log.

    """
    xbmc.log('[slideshow-BGM] ' + msg, xbmc.LOGINFO)


def notify(message, heading='[Slideshow-BGM]', icon=xbmcgui.NOTIFICATION_INFO, time=7000, sound=True):
    """Wrapper function of ``xbmcgui.Dialog().notification``.

    Args:
        message (str): message to show.
        heading (str): header text
        icon (str): icon. (default ``xbmcgui.NOTIFICATION_INFO``).
            Other built-in icons:
                - xbmcgui.NOTIFICATION_INFO
                - xbmcgui.NOTIFICATION_WARNING
                - xbmcgui.NOTIFICATION_ERROR
        time (int): time in milliseconds to show.
        sound (bool): whether to play notification sound. (default True)

    """

    xbmcgui.Dialog().notification(heading, message, icon, time, sound)


def show_dialog(message, heading='[Slideshow-BGM]', noLabel='Cancel', yesLabel='OK'):
    """ Wrapper function of ``xbmcgui.Dialog().yesno``.

    Args:
        messager (str): message to show.
        heading (str): header text.
        noLabel (str): text on No button.
        yesLabel (str): text on Yes button.

        .. note::
        ``defaultbutton`` argument does not seem to work.
        refer to https://codedocs.xyz/AlwinEsch/kodi/group__python___dialog.html#ga4541bc893b3ef70391cb299d6f522ccf

    Returns:
        bool: True in user chose Yes, False otherwise.

    """

    return xbmcgui.Dialog().yesno(heading, message, noLabel, yesLabel)


def create_playlist(BGM_dir):
    """Create a playlist file(m3u file) with the songs in ``BGM_dir``.

    Args:
        BGM_dir (str): Directory where to look for music files.

    Returns:
        str: The path of newly created playlist file if successful, ``None`` otherwise
        .. Warning::
            If there is no music file in the ``BGM_dir``, this function returns an empty playlist.

    """
    playlist_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
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
               + xbmcvfs.translatePath(addon.getAddonInfo('profile')),
               xbmcgui.NOTIFICATION_ERROR)
        return None

    if not count:
        notify('No music file in %s' % BGM_dir,
               xbmcgui.NOTIFICATION_WARNING)

    return playlist_file


def check_config():
    """Check addon settings to see if they are configured properly.

    Returns:
        str: empty string, i.e., '' if no problem found, applicable error string, otherwise.

    """
    _type = addon.getSetting('type')
    playlist = addon.getSetting('playlist')
    directory = addon.getSetting('directory')
    msg = ''

    if (_type == 'Playlist' and playlist == 'Not Selected') or \
            (_type == 'Directory' and directory == 'Not Selected'):
        msg = "You have not yet configured slideshow-BGM.\n"

    elif _type == 'Playlist' and not os.path.exists(playlist):
        msg = "Invalid playlist file: %s\n" % playlist

    elif _type == 'Directory' and not os.path.exists(directory):
        msg = "Invalid directory: %s\n" % directory

    return msg
