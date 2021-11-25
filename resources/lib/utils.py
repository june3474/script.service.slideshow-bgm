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

    message = message + '\nCheck the log.'
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


def create_playlist(bgm_dir):
    """Create a playlist file(m3u file) with the songs in ``bgm_dir``.

        .. Note: If ``filesystemencoding`` is 'askii(which seems to be default as of kodi v19.3')
        and filenames contain any non-ascii character, it raises UnicodeError to read/write filename as str.
        So, we seem to have no choice but to read/write filename as bytes until kodi's embedded python changes
        its default ``filesystemencoding`` to ``utf-8``.

    Args:
        bgm_dir (bytes): Directory where to look for music files.
                         Note the type of the argument is ``bytes``.

    Returns:
        str: The path of newly created playlist file if successful, ``None`` otherwise

    """
    playlist_dir = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    playlist_file = os.path.join(playlist_dir, 'bgm.m3u')
    music_file_exts = ('.mp2', '.mp3', '.wav', '.ogg', '.wma')

    count = 0
    try:
        with open(playlist_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U' + '\n' * 2)
            for root, dirs, files in os.walk(bgm_dir, followlinks=True):
                for filename in files:
                    if filename.decode('utf-8').lower().endswith(music_file_exts):
                        try:
                            path = os.path.join(root.decode('utf-8'), filename.decode('utf-8'))
                            f.write(path + '\n')
                            count += 1
                        except UnicodeError:
                            continue
    except (IOError,):
        notify("Failed to create a playlist file", icon=xbmcgui.NOTIFICATION_ERROR)
        log("Failed to create a playlist file in %s" % playlist_dir)
        if os.path.exists(playlist_file):
            os.remove(playlist_file)
        return None

    if not count:
        notify('No music file in\n %s' % bgm_dir, icon=xbmcgui.NOTIFICATION_WARNING)
        if os.path.exists(playlist_file):
            os.remove(playlist_file)
        return None

    log('playlist successfully created')
    return playlist_file


def check_config():
    """Check addon settings.

    This function also ensures a valid playlist is present.

    Returns:
        str: empty string, i.e., '' if no problem found, applicable error string, otherwise.

    """
    _type = addon.getSetting('type')
    # The path of playlist may contain non-ascii character
    playlist = addon.getSetting('playlist').encode('utf-8')
    # The path of bgm_dir may contain non-ascii character
    bgm_dir = addon.getSetting('directory').encode('utf-8')
    profile_path = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    playlist_file = os.path.join(profile_path, 'bgm.m3u')
    settings_file = os.path.join(profile_path, 'settings.xml')

    msg = ''

    if _type == 'Playlist':
        if playlist.decode('utf-8') == 'Not Selected':
            msg = "No background music set.\n"
        elif not os.path.exists(playlist.decode('utf-8')):
            msg = "Invalid playlist file: %s\n" % playlist.decode('utf-8')
    else:  # directory
        if bgm_dir.decode('utf-8') == 'Not Selected':
            msg = "No background music set.\n"
        elif not os.path.exists(bgm_dir.decode('utf-8')):
            msg = "Invalid directory: %s\n" % bgm_dir.decode('utf-8')
        elif not os.path.exists(playlist_file):
            create_playlist(bgm_dir)
        elif os.path.getmtime(playlist_file) < os.path.getmtime(settings_file):
            create_playlist(bgm_dir)
    if msg:
        log(msg)

    return msg
