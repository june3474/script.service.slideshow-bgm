# -*- coding: utf-8 -*-

import sys
import xbmc, xbmcaddon
from resources.lib.player import Player
from resources.lib.utils import check_config, log


log("Addon started")
if not check_config():
    sys.exit(1)

player = Player()
player.play_BGM()

# Ugly! but Blocking methods such as Tread.join or Lock.acquire do not work.
# They block all processes following and even callback functions of Player will not be called.
while xbmc.getCondVisibility('Slideshow.IsActive'):
    xbmc.sleep(1000)

player.stop()
log('Addon stopped')
