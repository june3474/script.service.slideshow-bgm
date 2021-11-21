# -*- coding: utf-8 -*-
"""Insert hooking-up tag into SlideShow.xml of the current skin

 This script automatically starts--if enabled-- when a user profile logs in or on Kodi startup,
 and stopped when the user profile logs out.
"""

import shutil
from resources.lib.binder import Binder
from resources.lib.utils import log, show_ok


binder = Binder()

if not binder.check_hooked():
    if binder.check_permission():
        shutil.copy(binder.target, binder.target + ".original")
        binder.insert_tag()
        log('The hook-up tag has been inserted to %s\n' % binder.target +
            ' and the original files was saved as %s' % binder.target+'.original.')
    else:  # installed && enabled && not hooked && not writable
        show_ok('Permission Error!\n\n' +
                'Can\'t write to "%s" file.\n\n' % binder.target +
                'You have to manually add the hooking-up tag.\n' +
                'Please refer to the README.org.')
        log('Inserting the hook-up tag to %s failed.' % binder.target)
