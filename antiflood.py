import time
import datetime
import logging
import telegram
from telegram.error import (TelegramError, Unauthorized, BadRequest,
		TimedOut, ChatMigrated, NetworkError)
from config import LOG_BAN_CHAT
from db import *

import log
logger = logging.getLogger(__name__)

_last_ban_log = 0

def ban_spammer(bot, userid, groupid):
	global _last_ban_log
	now = int(time.time())
	logger.info("ban: %s" % userid)
	try:
		bot.restrict_chat_member(chat_id=groupid,
				user_id=userid,
	#			until_date=now+24*60*60,
				can_send_messages=False,
				can_send_media_messages=False,
				can_send_other_messages=False,
				can_add_web_page_previews=False)
	except TelegramError as err:
		logger.warning("Error: %s" % str(err))
		return False
	# set_user_ban(userid, groupid, now+24*60*60)
	if now - _last_ban_log > 30:
		bot.send_message(chat_id=LOG_BAN_CHAT, text="Utente bannato: %s" % userid)
		_last_ban_log = now
	return True

def check_flood(bot, update, user_data, chat_data):
	userid = update.message.from_user.id
	username = update.message.from_user.username
	groupid = update.message.chat_id
	if 'spammers' in chat_data:
		if userid in chat_data['spammers']:
			ban_spammer(bot, userid, groupid)
			update.message.delete()
			return
		if (update.message.date - chat_data['spammers_ts']).total_seconds() > 300:
			try:
				del chat_data['spammers']
				del chat_data['spammers_ts']
			except:
				pass
	if update.message.text is not None and len(update.message.text.split("\n")) > 100:
		ban_spammer(bot, userid, groupid)
		update.message.delete()
		if not 'spammers' in chat_data:
			chat_data['spammers'] = [userid]
		else:
			chat_data['spammers'].append([userid])
		chat_data['spammers_ts'] = update.message.date
		if 'flood_msgs' in user_data:
			for msg in user_data['flood_msgs']:
				try:
					bot.delete_message(chat_id=update.message.chat_id,
							message_id=msg)
				except:
					pass
		for idx in ['last_msg_ts', 'last_msg_text', 'flood_count', 'flood_msgs']:
			try:
				del user_data[idx]
			except:
				pass
		return
	if not 'last_msg_ts' in user_data:
		user_data['last_msg_ts'] = update.message.date
		user_data['last_msg_text'] = update.message.text
		user_data['flood_msgs'] = [update.message.message_id]
		return
	if (update.message.date - user_data['last_msg_ts']).total_seconds() < 4:
		if not 'flood_msgs' in user_data:
			user_data['flood_msgs'] = [update.message.message_id]
		else:
			user_data['flood_msgs'].append([update.message.message_id])
		if not 'flood_count' in user_data:
			user_data['flood_count'] = 0
		else:
			user_data['flood_count'] += 1
	else:
		for idx in ['last_msg_ts', 'last_msg_text', 'flood_count', 'flood_msgs']:
			try:
				del user_data[idx]
			except:
				pass
		return
	user_data['last_msg_ts'] = update.message.date
	if update.message.text == user_data['last_msg_text']:
		user_data['flood_count'] += 3
	treshold = 7
	infos = None
	if username is not None and username != "":
		infos = get_user_info(username)
	if infos is not None:
		treshold = 15

	if user_data['flood_count'] > treshold:
		update.message.delete()
		if not 'spammers' in chat_data:
			chat_data['spammers'] = [userid]
		else:
			chat_data['spammers'].append([userid])
		chat_data['spammers_ts'] = update.message.date
		if not ban_spammer(bot, userid, groupid):
			return
		if 'flood_msgs' in user_data:
			for msg in user_data['flood_msgs']:
				try:
					bot.delete_message(chat_id=update.message.chat_id,
							message_id=msg)
				except:
					pass
		for idx in ['last_msg_ts', 'last_msg_text', 'flood_count', 'flood_msgs']:
			try:
				del user_data[idx]
			except:
				pass

__all__ = ["check_flood"]
