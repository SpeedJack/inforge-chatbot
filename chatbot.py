#!/usr/bin/env python3

import os
import sys
import time
import logging
import telegram
from telegram.error import (TelegramError, Unauthorized, BadRequest,
		TimedOut, ChatMigrated, NetworkError)
from config import BOT_TOKEN, GROUP_WHITELIST, PID_FILE, LOG_ERROR_CHAT
from db import open_db_connection, close_db_connection, register_member, get_user_info, set_not_restricted
from cmds import *
from antiflood import *
from filters import *
from memoized import memoized_collect
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters, Job

import log
logger = logging.getLogger(__name__)

_last_log_ts = 0
_last_welcome_ts = 0

def log_exception(extype, value, tb):
	logger.exception("Unhandled Exception: {0}".format(str(value)))

def error(bot, update, error):
	global _last_log_ts
	logger.error('Update "%s" caused error "%s"' % (update, error))
	if isinstance(error, TimedOut):
		return
	now = time.time()
	try:
		if (now - _last_log_ts) > 300:
			bot.send_message(chat_id=LOG_ERROR_CHAT,
					text="An error occured. Check log file.")
			_last_log_ts = now
	except TelegramError:
		logger.error("Can not write to LOG_ERROR_CHAT")

def new_member(bot, update):
	global _last_welcome_ts
	uid = None
	if update.message.new_chat_member:
		uid = update.message.new_chat_member.id
	checked = False
	verified = True
	for u in update.message.new_chat_members:
		if u.id == uid:
			checked = True
		register_member(u.id, update.message.chat_id)
		infos = None
		if u.username is not None and u.username != "":
			infos = get_user_info(u.username)
		if infos is None:
			verified = False
			bot.restrict_chat_member(chat_id=update.message.chat_id,
					user_id=u.id,
					can_send_messages=True,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
	if update.message.new_chat_member and not checked:
		username = update.message.new_chat_member.username
		register_member(uid, update.message.chat_id)
		infos = None
		if username is not None and username != "":
			infos = get_user_info(username)
		if infos is None:
			verified = False
			bot.restrict_chat_member(chat_id=update.message.chat_id,
					user_id=uid,
					can_send_messages=True,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
	now = int(time.time())
	if not verified and now - _last_welcome_ts > 30:
		_last_welcome_ts = now
		bot.send_message(chat_id=update.message.chat_id,
				text="Ciao! per poter inviare messaggi multimediali devi prima verificare il tuo account. Contattami in privato (@InforgeChat_BOT) per completare la procedura!",
				reply_to_message_id=update.message.message_id)


def old_member(bot, update):
	userid = update.message.from_user.id
	username = update.message.from_user.username
	register_member(userid, update.message.chat_id)
	infos = None
	if username is not None and username != "":
		infos = get_user_info(username)
	if infos is None:
		bot.restrict_chat_member(chat_id=update.message.chat_id,
				user_id=userid,
				can_send_messages=True,
				can_send_media_messages=False,
				can_send_other_messages=False,
				can_add_web_page_previews=False)

def remove_bot(bot, update):
	uid = None
	if update.message.new_chat_member:
		uid = update.message.new_chat_member.id
	checked = False
	for u in update.message.new_chat_members:
		if u.id == uid:
			checked = True
		if u.username and u.username[-3:].lower() == "bot":
			bot.restrict_chat_member(chat_id=update.message.chat_id,
					user_id=u.id,
					can_send_messages=False,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
			bot.kick_chat_member(chat_id=update.message.chat_id,
					user_id=u.id)
	if update.message.new_chat_member and not checked:
		username = update.message.new_chat_member.username
		if username and username[-3:].lower() == "bot":
			bot.restrict_chat_member(chat_id=update.message.chat_id,
					user_id=uid,
					can_send_messages=False,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
			bot.kick_chat_member(chat_id=update.message.chat_id,
					user_id=uid)

	update.message.delete()

def leave_group(bot, update):
	logger.info("Group %d is not whitelisted" % update.message.chat_id)
	bot.leave_chat(chat_id=update.message.chat_id)

def collect(bot, update):
	memoized_collect()

def debug_log(bot, update):
	logger.debug("Received update: %s" % update)

def main():
	bot = telegram.Bot(token=BOT_TOKEN)
	updater = Updater(token=BOT_TOKEN)
	dispatcher = updater.dispatcher

	open_db_connection()

	filter_admin = FilterAdmin(bot)
	filter_whitelist = Filters.chat(chat_id=GROUP_WHITELIST)

	start_handler = CommandHandler("start", show_help,
			filters=Filters.private)
	help_handler = CommandHandler("help", show_help,
			filters=Filters.private)
	verify_handler = CommandHandler("verify", show_help,
			filters=Filters.private)
	whoami_handler = CommandHandler("whoami", whoami,
			filters=Filters.private)
	whois_handler = CommandHandler("whois", whois,
			filters=Filters.group & filter_whitelist &
			Filters.reply)
	ban_handler = CommandHandler("ban", ban_user, pass_args=True,
			filters=Filters.group & filter_whitelist &
			Filters.reply & filter_admin)
	unban_handler = CommandHandler("unban", unban_user,
			pass_args=True, pass_chat_data=True,
			filters=Filters.group & filter_whitelist &
			filter_admin)
	remove_keyboard_handler = CommandHandler("remove_keyboard",
			remove_keyboard,
			filters=Filters.group & filter_whitelist &
			filter_admin)
	restart_handler = CommandHandler("restart", restart,
			filters=Filters.group & filter_whitelist &
			filter_admin)
	force_collect_handler = CommandHandler("force_collect", force_collect,
			filters=Filters.group & filter_whitelist &
			filter_admin)
#	purge_handler = CommandHandler("purge", purge,
#			filters=Filters.group & filter_whitelist &
#			filter_admin)
	kbd_action_handler = MessageHandler(Filters.private, kdb_action)

	botadd_handler = MessageHandler(Filters.group & filter_whitelist &
			Filters.status_update.new_chat_members &
			filter_added_bot & ~filter_admin,
			remove_bot)
	userjoin_handler = MessageHandler(Filters.group & filter_whitelist &
			Filters.status_update.new_chat_members,
			new_member)
	antiflood_handler = MessageHandler(Filters.group & filter_whitelist &
			~Filters.status_update.new_chat_members &
			~Filters.status_update.left_chat_member &
			~filter_admin,
			check_flood, pass_user_data=True, pass_chat_data=True)

	oldmember_handler = MessageHandler(Filters.group & filter_whitelist &
			~filter_registered & ~filter_admin,
			old_member)

	whitelist_handler = MessageHandler(Filters.group & ~filter_whitelist,
			leave_group)
	pinger_handler = CommandHandler("ping", ping,
			filters=Filters.private | (Filters.group &
				filter_whitelist & filter_admin))
	collector_handler = MessageHandler(Filters.all, collect)
	debug_log_handler = MessageHandler(Filters.all, debug_log)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(verify_handler)
	dispatcher.add_handler(whoami_handler)
	dispatcher.add_handler(whois_handler)
	dispatcher.add_handler(ban_handler)
	dispatcher.add_handler(unban_handler)
	dispatcher.add_handler(remove_keyboard_handler)
	dispatcher.add_handler(restart_handler)
	dispatcher.add_handler(force_collect_handler)
#	dispatcher.add_handler(purge_handler)
	dispatcher.add_handler(kbd_action_handler)
	dispatcher.add_handler(botadd_handler, 1)
	dispatcher.add_handler(userjoin_handler, 1)
	dispatcher.add_handler(antiflood_handler, 1)
	dispatcher.add_handler(oldmember_handler, 2)
	dispatcher.add_handler(whitelist_handler, 97)
	dispatcher.add_handler(pinger_handler, 97)
	dispatcher.add_handler(collector_handler, 98)
	dispatcher.add_handler(debug_log_handler, 99)

	dispatcher.add_error_handler(error)

	logger.info("GetMe: %s" % bot.get_me())

	updater.start_polling()
	updater.idle()
	bot.send_message(chat_id=LOG_ERROR_CHAT,
			text="Shutting down...")
	close_db_connection()
	logger.info("Shutting down...")

if __name__ == "__main__":
	if os.path.isfile(PID_FILE):
		with open(PID_FILE, "r") as f:
			pid = f.readline()
			try:
				os.kill(int(pid), 0)
			except OSError:
				pass
			else:
				logger.warning("An instance of the bot is already running. Exiting...")
				sys.exit()

	pid = os.getpid()
	with open(PID_FILE, "w") as f:
		f.write(str(pid))

	sys.excepthook = log_exception

	main()

	os.remove(PID_FILE)
	time.sleep(0.2)
