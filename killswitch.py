import time
import datetime
import logging
import telegram

import log
logger = logging.getLogger(__name__)

var_kill_switch = False

def check_killswitch(bot, update):
	userid = update.message.from_user.id
	if var_kill_switch:
		try:
			update.message.delete()
		except:
			pass

def change_var():
	global var_kill_switch
	var_kill_switch = not var_kill_switch
	return var_kill_switch

__all__ = ["check_killswitch", "change_var"]