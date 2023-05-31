# -*- coding: utf-8 -*-
"""Helper functions"""

import os
import xbmc, xbmcgui, xbmcvfs
from . import addon, addonName


def log(msg):
    """Wrapper function for ``xbmcgui.log()``.

    Args:
        msg (str): message to log.

    """
    xbmc.log('[slideshow-bgm] ' + msg, xbmc.LOGINFO)


def notify(message, heading=addonName, icon=xbmcgui.NOTIFICATION_INFO, time=7000, sound=True):
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


def show_yesno(message, heading=addonName, noLabel='Cancel', yesLabel='OK'):
    """ Wrapper function of ``xbmcgui.Dialog().yesno``.

    Args:
        message (str): message to show.
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


def show_ok(message, heading=addonName):
    """ Wrapper function of ``xbmcgui.Dialog().ok``.

    Args:
        message (str): message to show.
        heading (str): header text.

    Returns:
        bool: True if 'OK' was pressed, False otherwise.

    """

    return xbmcgui.Dialog().ok(heading, message)


def create_playlist(bgm_dir, file_name="bgm.m3u"):
    """Create a playlist file(m3u file) with the songs in ``bgm_dir``.

    .. Note: If ``filesystemencoding`` is 'askii(which seems to be default 
            since kodi v19.3') and filenames contain any non-ascii character, 
            it raises UnicodeError to read/write filename as str.
            So, we need to read/write filename as bytes.
            https://forum.kodi.tv/showthread.php?tid=366245

    Args:
        bgm_dir (bytes): Directory where to look for music files.

    Returns:
        str: The path of the newly created playlist file if successful, 
        ``None`` otherwise

    """
    playlist_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    playlist_file = os.path.join(playlist_dir, file_name)
    music_file_exts = ('.mp2', '.mp3', '.wav', '.ogg', '.wma')

    count = 0
    try:
        with open(playlist_file, mode='w', encoding='utf-8') as f:
            f.write('#EXTM3U' + os.linesep * 2)
            # os.walk() returns bytes if the given argument is bytes
            for root, dirs, files in os.walk(bgm_dir, followlinks=True):
                root_str = root.decode('utf-8')
                for file in files:
                    file_str = file.decode('utf-8')
                    if file_str.lower().endswith(music_file_exts):
                        f.write(os.path.join(root_str, file_str) + os.linesep)
                        count += 1
    except (IOError,):
        log("Failed to create a playlist, %s" % playlist_file)
        return None

    if not count:
        log('No music file in %s' % bgm_dir)
        return None

    log("Created a playlist, %s" % playlist_file)
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
        msg = "No background music is set."
    # We don't use os.path.exists() due to kodi's 'filesystemencoding'
    elif _type == 'Playlist' and not xbmcvfs.exists(playlist):
        msg = "Invalid playlist file: %s." % playlist
    elif _type == 'Directory' and not xbmcvfs.exists(directory):
        msg = "Invalid directory: %s." % directory

    return msg
