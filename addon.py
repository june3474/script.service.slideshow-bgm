# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import xbmc, xbmcaddon
from resources.lib.player import Player
from resources.lib.utils import create_playlist, check_config, log


log("Addon started")
if not check_config():
    sys.exit(1)

player = Player()
player.play_BGM()
while xbmc.getCondVisibility('Slideshow.IsActive'):
        xbmc.sleep(1000)

player.stop()
log('Addon stopped')
