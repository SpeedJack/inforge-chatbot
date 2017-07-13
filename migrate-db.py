#!/usr/bin/python3 -u

import urllib.request
from urllib.error import HTTPError
import json
import time
import telegram
from telegram.error import TelegramError
import sqlite3 as sqlite
from config import BOT_TOKEN
from db import open_db_connection, close_db_connection, get_db_connection

def insert_user(uid, name, tg):
	print("ROW: " + str(uid), name, tg, sep="|")
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("INSERT INTO users(ifuserid, ifusername, tgusername, restricted) VALUES(?, ?, ?, 0)",
			(uid, name, tg))
	conn.commit()
	cur.close()

def ask_inforge(userid):
	jsonstr = urllib.request.urlopen("https://www.inforge.net/xi/_api.php?action=getUsers&value=" + str(userid) + "&hash=***REMOVED***").read().decode("utf-8")
	data = json.loads(jsonstr)
	if not data or len(data) == 0:
		print("No data: account deleted on inforge")
		raise Exception
	found = False
	for u in data:
		uid = int(u['user_id'])
		if uid != userid:
			continue
		found = True
		username = str(u['username'])
		if not username or username == "":
			print("No inforge username... wtf")
			raise Exception
		tg = str(u['custom_fields']['Telegram'])

	if found:
		return [uid, username, tg]
	print("user not found on inforge:", str(userid))
	raise Exception


_cur_line = 0
def process(bot, line):
	global _cur_line
	_cur_line += 1
	print("Processing:", line, end="")
	tg, uid, name = line.rstrip("\n").split(",", 2)
	tg = int(tg)
	uid = int(uid)
	if not tg or not uid or not name or name == "":
		print("Invalid format line:", str(_cur_line))
		return
	try:
		userid, username, tgusername = ask_inforge(uid)
	except HTTPError as e:
		if e.code == 400:
			print("Account not found on inforge")
			with open("to-contact.lst", "a") as f:
				print(tg, file=f)
		else:
			print("HTTPError")
		return
	except Exception as err:
		print("Error in ask_inforge():", str(err))
		return
	if not tgusername or tgusername == "":
		print("No telegram field on inforge")
		with open("to-contact.lst", "a") as f:
			print(tg, file=f)
		return
	print("Inforge data:", str(userid), username, tgusername)
	cm = None
	try:
		cm = bot.get_chat_member(chat_id=-1001055827794,
				user_id=tg)
	except TelegramError as err:
		print("Error get_chat_member():", str(err))
	if cm is not None and cm.user.username != tgusername:
		print("tg username changed:", tgusername, "-->", cm.user.username)
		with open("to-contact.lst", "a") as f:
			print(tg, file=f)
		return
	insert_user(userid, username, tgusername)



if __name__ == "__main__":
	open_db_connection()
	bot = telegram.Bot(token=BOT_TOKEN)
	with open("users.csv", "r") as f:
		for line in f:
			process(bot, line)
			print("---")
			time.sleep(1)
	close_db_connection()
