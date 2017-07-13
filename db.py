import logging
import time
import sqlite3 as sqlite
from config import DATABASE_FILE
from memoized import memoized

import log
logger = logging.getLogger(__name__)

_connection = None

def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

def close_db_connection():
	global _connection
	if _connection is not None:
		logger.info("Closing database connection")
		_connection.close()
		_connection = None

def open_db_connection():
	global _connection
	if _connection is not None:
		logger.info("Opening database connection")
		close_db_connection()
	_connection = sqlite.connect(DATABASE_FILE, check_same_thread=False)
	_connection.row_factory = dict_factory

def get_db_connection():
	global _connection
	if _connection is None:
		open_db_connection()
	return _connection

@memoized(timeout=365*24*60*60)
def register_member(userid, group):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("INSERT OR IGNORE INTO members(userid, groupid, banned_until) VALUES(?, ?, NULL)",
			(userid, group))
	conn.commit()
	cur.close()

@memoized(timeout=100*24*60*60)
def is_registered(userid, group):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("SELECT COUNT(*) AS num FROM members WHERE userid=? AND groupid=?",
			(userid, group))
	res = cur.fetchone()
	cur.close()
	return res['num'] > 0

def get_banned_members():
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM members WHERE banned_until IS NOT NULL")
	res = cur.fetchall()
	cur.close()
	return res

def set_user_ban(userid, group, until):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("INSERT OR REPLACE INTO members(userid, groupid, banned_until) VALUES(?, ?, ?)",
			(userid, group, until))
	conn.commit()
	cur.close()

def remove_user_ban(userid, group):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("UPDATE members SET banned_until=NULL WHERE userid=? AND groupid=?",
			(userid, group))
	conn.commit()
	cur.close()

@memoized(timeout=5*60, refresh_on_access=True)
def get_user_info(username):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE tgusername=?", (username,))
	res = cur.fetchone()
	cur.close()
	return res

def set_not_restricted(ifuserid):
	conn = get_db_connection()
	cur = conn.cursor()
	cur.execute("UPDATE users SET restricted=0 WHERE ifuserid=?",
			(ifuserid,))
	conn.commit()
	cur.close()

__all__ = ["close_db_connection", "open_db_connection", "get_db_connection",
		"register_member", "set_user_ban", "remove_user_ban",
		"get_user_info", "set_not_restricted", "get_banned_members"]
