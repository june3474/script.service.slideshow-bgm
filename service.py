# -*- coding: utf-8 -*-
"""Insert hooking-up tag into and check settings

 This script automatically starts--if enabled-- when a user profile logs in or on Kodi startup,
 and stopped when the user profile logs out.
"""

import sys
import shutil
import xbmcgui
from resources.lib import addon
from resources.lib.binder import Binder
from resources.lib.utils import log, notify, show_yesno, check_config

# check configuration
while True:
    msg = check_config()
    if msg == '':  # configuration is OK
        log('Configuration check, OK!')
        break
    else:
        if show_yesno(msg + '\nProceed to configure slideshow-bgm?'):
            addon.openSettings()
        else:
            log('Aborted by user')
            sys.exit(1)

# check interlocking with skin
binder = Binder()
if not binder.check_hooked():
    if binder.check_permission():
        shutil.copy(binder.target, binder.target + ".original")
        binder.insert_tag()
        log('The interlocking tag has been inserted to %s\n' % binder.target +
            'and the original file was saved as %s' % binder.target+'.original')
    else:  # installed && enabled && not hooked && not writable
        notify('Unable to interlock with the skin', icon=xbmcgui.NOTIFICATION_WARNING)
        log('Failed to write the interlocking tag into %s\n' % binder.target +
            'Check your permission')
        sys.exit(1)
else:
    log('Interlock check, OK!')
