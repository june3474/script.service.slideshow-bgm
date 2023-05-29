# -*- coding: utf-8 -*-

import sys
import xbmc, xbmcgui
from resources.lib import addon
from resources.lib.player import Player
from resources.lib.utils import check_config, show_yesno, log, notify


log("addon.py started.")

# check configuration
while True:
    msg = check_config()
    if msg == '':  # configuration is OK
        break
    else:
        if show_yesno(msg 
                      + '\nClick OK to proceed to Slideshow-bgm settings'
                      + '\nCancel will abort Slideshow-bgm'):
            addon.openSettings()
        else:
            log('Aborted by user.')
            sys.exit(1)

try:
    player = Player()
except ValueError as E:
    notify(E.__str__() + " Check the log.", icon=xbmcgui.NOTIFICATION_ERROR)

player.play_bgm()

# Ugly! but Blocking methods such as Tread.join or Lock.acquire does not work.
# They block all processes following and even callback functions of Player.
# There seems to be no other way as of May 2023.
# https://kodi.wiki/view/Service_add-ons
monitor = xbmc.Monitor()
while True:
    if not xbmc.getCondVisibility('Slideshow.IsActive') or monitor.abortRequested():
        break
    else:
        xbmc.sleep(500)

player.stop()

log('addon.py ended.')
