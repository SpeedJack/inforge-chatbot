#!/usr/bin/env python

def ask_inforge(userid):
	jsonstr = urllib.request.urlopen("https://www.inforge.net/xi/_api.php?action=getUsers&value=" + str(userid) + "&hash=***REMOVED***").read().decode("utf-8")
	data = json.loads(jsonstr)
	if not data or len(data) == 0:
		raise Exception
	found = False
	for u in data:
		uid = int(u['user_id'])
		if uid != userid:
			continue
		found = True
		username = str(u['username'])
		if not username or username == "":
			raise Exception
		tg = str(u['custom_fields']['Telegram'])

	if found:
		return [uid, username, tg]
	raise Exception

def process(ifuserid):
	# for each user in users, check if inforge username is changed: if the
	# account has been deleted, remove from users; if the username has
	# changed, update the username on users; otherwise, do nothing. Repeat
	# in cronjob every week
	pass
