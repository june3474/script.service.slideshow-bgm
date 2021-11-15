# -*- coding: utf-8 -*-
 
import xbmc
from resources.lib import addonId
from resources.lib.binder import Binder
from resources.lib.utils import log, show_dialog

binder = Binder()

if not binder.check_hooked():
    binder.insert_tag()

