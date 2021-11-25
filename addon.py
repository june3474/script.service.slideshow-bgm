# -*- coding: utf-8 -*-

import sys
import xbmc
from resources.lib.player import Player
from resources.lib.utils import log, check_config, notify


log("addon.py started")

# make sure a valid playlist exists and up-to-date
if check_config():
    notify('Invalid settings')
    sys.exit(1)

player = Player()
player.play_bgm()

# Ugly! but Blocking methods such as Tread.join or Lock.acquire do not work.
# They block all processes following and even callback functions of Player seem not to be called.
while xbmc.getCondVisibility('Slideshow.IsActive'):
    xbmc.sleep(500)

player.stop()

log('addon.py ended')
