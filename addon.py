# -*- coding: utf-8 -*-

import sys
import xbmc
from resources.lib import addon
from resources.lib.player import Player
from resources.lib.utils import check_config, show_yesno, log


log("addon.py started.")

# check configuration
while True:
    msg = check_config()
    if msg == '':  # configuration is OK
        break
    else:
        if show_yesno(msg + '\nClick Yes to proceed to Slideshow-bgm settings'
                      + '\nCancel will abort Slideshow-bgm'):
            addon.openSettings()
        else:
            log('Aborted by user.')
            sys.exit(1)

player = Player()
player.play_bgm()

# Ugly! but Blocking methods such as Tread.join or Lock.acquire do not work.
# They block all processes following and even callback functions of Player seem not to be called.
while xbmc.getCondVisibility('Slideshow.IsActive'):
    xbmc.sleep(500)

player.stop()

log('addon.py ended.')
