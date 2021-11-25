# -*- coding: utf-8 -*-
"""Insert hooking-up tag into and check settings

 This script automatically starts--if enabled-- when a user profile logs in or on Kodi startup,
 and stopped when the user profile logs out.
"""

import sys
import shutil
import xbmcgui
from resources.lib import addon, addonName
from resources.lib.binder import Binder
from resources.lib.utils import log, notify, show_yesno, check_config, just_installed

# prompt for config after being installed
if just_installed():
    if show_yesno('Proceed to configure %s now?' % addonName):
        addon.openSettings()
    else:
        log('Configuration aborted by user')

# check configuration
if check_config():
    notify('Invalid settings', icon=xbmcgui.NOTIFICATION_WARNING)
else:
    log('Configuration check, OK!')

# check interlocking with skin
binder = Binder()
if binder.check_hooked():
    log('Interlock check, OK!')
else:
    if binder.check_permission():
        shutil.copy(binder.target, binder.target + ".original")
        binder.insert_tag()
        log('The interlocking tag has been inserted to %s\n' % binder.target +
            'and the original file was saved as %s' % binder.target+'.original')
    else:  # installed && enabled && not hooked && not writable
        notify('Unable to interlock with the skin', icon=xbmcgui.NOTIFICATION_ERROR)
        log('Failed to write the interlocking tag into %s\n' % binder.target +
            'Check your permission')
