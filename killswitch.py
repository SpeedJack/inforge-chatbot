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
			bot.send_message(chat_id=userid, text="Al momento non è possibile inviare messaggi nel gruppo!")
		except:
			pass
		finally:
			update.message.delete()

def change_var():
	global var_kill_switch
	var_kill_switch = not var_kill_switch
	return var_kill_switch

__all__ = ["check_killswitch", "change_var"]