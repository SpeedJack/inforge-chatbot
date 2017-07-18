#!/usr/bin/env python3

import os
import sys
import signal
import time
import logging
import telegram
from telegram.error import TelegramError, Unauthorized, BadRequest
from config import BOT_TOKEN
from memoized import memoized
from db import open_db_connection, close_db_connection, get_temp_banned_members, get_user_info, remove_user_ban, set_user_ban

import log
logger = logging.getLogger("update-members")

PID_FILE = "update-members.pid"

def sighandler():
	try:
		close_db_connection()
		os.remove(PID_FILE)
	except:
		pass
	time.sleep(0.2)
	sys.exit()

def main():
	bot = telegram.Bot(token=BOT_TOKEN)
	open_db_connection()
	while True:
		now = int(time.time())
		next_time = now
		data = get_temp_banned_members()
		for m in data:
			if m['banned_until'] > now:
				if m['banned_until'] > next_time:
					next_time = m['banned_until']
				continue
			try:
				cm = bot.get_chat_member(chat_id=m['groupid'],
						user_id=m['userid'])
				if cm.status == "restricted" and cm.until_date is not None:
					set_user_ban(m['userid'], m['groupid'], cm.until_date.total_seconds())
					continue
				if cm.status != "member":
					remove_user_ban(m['userid'], m['groupid'])
					continue
				infos = None
				if cm.user.username is not None and cm.user.username != "":
					infos = get_user_info(cm.user.username)
				if infos is None:
					bot.restrict_chat_member(
							chat_id=m['groupid'],
							user_id=m['userid'],
							can_send_messages=True,
							can_send_media_messages=False,
							can_send_other_messages=False,
							can_add_web_page_previews=False)
					logger.info("Restricted: %s (%s)" % (repr(cm.user.username), str(m['userid'])))
				remove_user_ban(m['userid'], m['groupid'])
			except (Unauthorized, BadRequest):
				remove_user_ban(m['userid'], m['groupid'])
			except:
				pass
			finally:
				time.sleep(0.1)
		renow = int(time.time())
		if next_time == now or next_time > renow+10*60 or next_time <= renow:
			next_time = renow+10*60-3
		next_time -= renow
		memoized().collect()
		logger.debug("Next run: " + str(next_time+3))
		time.sleep(next_time+3)



if __name__ == "__main__":
	if os.path.isfile(PID_FILE):
		with open(PID_FILE, "r") as f:
			pid = f.readline()
			try:
				os.kill(int(pid), 0)
			except OSError:
				pass
			else:
				logger.warning("An instance of update-members is already running. Exiting...")
				sys.exit()

	pid = os.getpid()
	with open(PID_FILE, "w") as f:
		f.write(str(pid))
	try:
		signal.signal(signal.SIGINT, sighandler)
		signal.signal(signal.SIGTERM, sighandler)
	except (OSError, RuntimeError, ValueError):
		pass
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		try:
			close_db_connection()
			os.remove(PID_FILE)
		except:
			pass
		time.sleep(0.2)
		sys.exit()
