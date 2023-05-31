# -*- coding: utf-8 -*-
"""Insert interconnection tag into skin and check settings

 This script automatically starts--if the addon is enabled--when a user profile
 logs in or on Kodi startup, and stopped when the user profile logs out.

"""

import sys
import shutil
import xbmcgui
from resources.lib.skinconnector import SkinConnector
from resources.lib.utils import log, notify, check_config
from resources.lib import addonName

msg = ''

# check configuration
msg = check_config()
if msg:
    log('Configuration check, Failed: %s' % msg)
else:
    log('Configuration check, OK!')

# check interconnection to skin
connector = SkinConnector()
if connector.check_hooked():
    log('Skin connection check, OK!')
else:
    if connector.check_permission():
        shutil.copy(connector.target, connector.target + ".original")
        connector.insert_tag()
        log('The interconnetion tag has been inserted to %s\n' % connector.target +
            'The original file was saved as %s' % connector.target + '.original')
    else:  # installed && enabled && not hooked && not writable
        log('Failed to write the interconnecting tag into %s' % connector.target)
        if msg:
             msg = msg + ' & Skin interconnection failed.'
        else:
            msg = 'Skin interconnection failed.'
        
if msg:
    notify(msg, heading=addonName+" Error", icon=xbmcgui.NOTIFICATION_ERROR)
