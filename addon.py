# -*- coding: utf-8 -*-

import sys
import xbmc, xbmcaddon
from resources.lib.player import Player
from resources.lib.utils import check_config, show_dialog, log


log("Addon started.")

while True:
    msg = check_config()
    if msg == '':
        break
    else:
        if show_dialog(msg + '\nClick Yes to proceed to Slideshow-BGM settings'
                           + '\nCancel will abort Slideshow-BGM'):
            xbmcaddon.Addon('script.slideshow-BGM').openSettings()
        else:
            log('Aborted by user.')
            sys.exit(1)

player = Player()
player.play_BGM()

# Ugly! but Blocking methods such as Tread.join or Lock.acquire do not work.
# They block all processes following and even callback functions of Player will not be called.
while xbmc.getCondVisibility('Slideshow.IsActive'):
    xbmc.sleep(1000)

player.stop()

log('Addon exits.')
