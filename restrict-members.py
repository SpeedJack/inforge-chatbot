#!/usr/bin/env python3

import time
import telegram
from telegram.error import TelegramError
from db import open_db_connection, close_db_connection, register_member, get_user_info
from config import BOT_TOKEN


def apply_restriction(userid):
	group = -1001055827794
	print("Processing:", line, end="")
	cm = None
	try:
		cm = bot.get_chat_member(chat_id=group,
				user_id=userid)
	except TelegramError as err:
		print("Error get_chat_member():", str(err))
		return
	if cm.status == "restricted" or cm.status == "kicked" or cm.status == "left" or cm.status == "administrator" or cm.status == "creator":
		#double check
		print("Not member: skipping")
		return
	if cm.status == "member" and (cm.can_send_messages is None or cm.can_send_messages == True):
		register_member(userid, group)
	else:
		print("Not member or can not send messages: skipping")
		return
	if cm is None or cm.user.username is None or cm.user.username == "":
		try:
			bot.restrict_chat_member(chat_id=group,
					user_id=userid,
					can_send_messages=True,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
		except TelegramError:
			print("Error restrict_chat_member():", str(err))
			pass
		return
	infos = get_user_info(cm.user.username)
	if infos is None:
		try:
			bot.restrict_chat_member(chat_id=group,
					user_id=userid,
					can_send_messages=True,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
		except TelegramError as err:
			print("Error restrict_chat_member():", str(err))
			pass
		finally:
			return
	print("User verified: skipping")

if __name__ == "__main__":
	bot = telegram.Bot(token=BOT_TOKEN)
	open_db_connection()
	with open("members.lst", "r") as f:
		for line in f:
			apply_restriction(int(line.rstrip("\n")))
			print("---")
			time.sleep(0.5)
	close_db_connection()
