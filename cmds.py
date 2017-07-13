import os
import datetime
import time
import sys
import logging
import telegram
from telegram.error import (TelegramError, Unauthorized, BadRequest,
		TimedOut, ChatMigrated, NetworkError)
from config import PID_FILE, GROUP_WHITELIST
from db import *
from memoized import memoized, memoized_collect

import log
logger = logging.getLogger(__name__)

_kbd = [[telegram.KeyboardButton(text=u"☑️ Verifica Account")],
	[telegram.KeyboardButton(text=u"👤 Info su di me")]]
_rkm = telegram.ReplyKeyboardMarkup(_kbd)

def show_help(bot, update):
	bot.send_message(chat_id=update.message.chat_id,
			text="Ciao! Io sono il bot che gestisce il gruppo *Inforge Chat* (@inforgechat) e il gruppo *Inforge Hearthstone* (@ifheartstonechat)!\nTramite me puoi verificare il tuo account inforge, dopodiché potrai inviare messaggi multimediali nei gruppi! Clicca su `Verifica Account` per procedere.\n\n_Per evitare ban per flood, non scrivere troppo velocemente nel gruppo: cerca di scrivere tutto quello che hai da dire in un unico messaggio, e aspetta un po' di tempo tra un messaggio e l'altro_",
			parse_mode=telegram.ParseMode.MARKDOWN,
			reply_markup=_rkm)

def prepare_whois_message(userid, username):
	infos = None
	if username is not None and username != "":
		infos = get_user_info(username)
	if infos is None:
		return "<b>utente:</b> " + str(username) + "\n" +\
			"<b>tg userid:</b> " + str(userid) + "\n" +\
			"<i>Account Inforge NON Collegato!</i>"
	else:
		return "<b>utente:</b> " + str(username) + "\n" +\
			"<b>telegram userid:</b> " + str(userid) + "\n" +\
			"<i>Account Inforge Collegato!</i>" + "\n" +\
			"<b>inforge username:</b> " +\
			infos["ifusername"] + "\n" +\
			"<b>inforge userid:</b> " + str(infos["ifuserid"])

def whoami(bot, update):
	userid = update.message.from_user.id
	username = update.message.from_user.username
	bot.send_message(chat_id=update.message.chat_id,
			text=prepare_whois_message(userid, username),
			parse_mode=telegram.ParseMode.HTML,
			reply_markup=_rkm)

def whois(bot, update):
	userid = update.message.reply_to_message.from_user.id
	username = update.message.reply_to_message.from_user.username
	try:
		bot.send_message(chat_id=update.message.from_user.id,
				text=prepare_whois_message(userid, username),
				parse_mode=telegram.ParseMode.HTML,
				reply_markup=_rkm)
	except (Unauthorized, BadRequest):
		pass
	finally:
		update.message.delete()

def remove_restriction(bot, userid):
	for grp in GROUP_WHITELIST:
		try:
			cm = bot.get_chat_member(chat_id=grp, user_id=userid)
			if cm.status == 'restricted' and cm.can_send_messages == True:
				bot.restrict_chat_member(chat_id=grp,
						user_id=userid,
						can_send_messages=True,
						can_send_media_messages=True,
						can_send_other_messages=True,
						can_add_web_page_previews=True)
		except TelegramError:
			pass

def show_verify_info(bot, update):
	username = update.message.from_user.username
	userid = update.message.from_user.id
	infos = None
	if username is not None and username != "":
		infos = get_user_info(username, no_cache=True)

	if infos is None:
		if username is None or username == "":
			username = "non hai ancora scelto un username! Devi inserirlo dalle impostazioni di Telegram!"

		bot.send_message(chat_id=userid,
				text="Devi ancora verificare il tuo account!\n\nPer completare la verifica ti basta accedere al tuo account [inforge.net](https://www.inforge.net/xi/) e dirigerti nella pagina [Informazioni di Contatto](https://www.inforge.net/xi/account/contact-details) del tuo profilo. Qui, dovrai inserire il tuo username Telegram (" + username + ") nel campo `Telegram` e quindi cliccare su `Salva Modifica`. Finito!\n\nRicorda che dopo può essere necessario un po' di tempo (solitamente qualche minuto) prima che la modifica venga registrata (puoi _forzare_ l'aggiornamento cliccando nuovamente su `Verifica Account`). Se cambi il tuo username Telegram, ricordati di cambiarlo anche su Inforge (o il tuo account verrà nuovamente bloccato).\n\nIn caso di problemi, contatta il [Supporto Ticket](https://www.inforge.net/xi/support-tickets/open) nel Reparto Generale!",
				parse_mode=telegram.ParseMode.MARKDOWN,
				reply_markup=_rkm)
		return

	if infos['restricted']:
		remove_restriction(bot, userid)
		set_not_restricted(infos['ifuserid'])
	bot.send_message(chat_id=userid,
			text="Il tuo account risulta correttamente verificato! Puoi inviare messaggi multimediali nei gruppi!",
			reply_markup=_rkm)

def get_sec(time_str):
	if time_str is None or time_str == "":
		return None
	try:
		field = [0, 0, 0, 0]
		sep = [ 'M', 'd', 'h', 'm' ]
		for i in range(0, 4):
			try:
				field[i], time_str = time_str.split(sep[i], 1)
			except ValueError:
				field[i] = 0
		return (((int(field[0])*30 +
			int(field[1]))*24 +
			int(field[2]))*60 +
			int(field[3]))*60
	except:
		return None

def ban_user(bot, update, args):
	group = update.message.chat_id
	userid = update.message.reply_to_message.from_user.id
	if not args or "forever" in args[0]:
		try:
			bot.restrict_chat_member(chat_id=group,
					user_id=userid,
					can_send_messages=False,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
		except TelegramError as err:
			bot.send_message(chat_id=update.message.from_user.id,
					text=str(err))
			update.message.delete()
			return;
		until = None
	else:
		secs = get_sec(args[0])
		if secs is None or secs < 60 or secs > 365*24*60*60:
			bot.send_message(chat_id=update.message.from_user.id,
					text="Durata del ban non valida. Riprova!")
			update.message.delete()
			return
		else:
			until = int(time.time()) + secs
			try:
				bot.restrict_chat_member(chat_id=group,
						user_id=userid,
						until_date=until,
						can_send_messages=False,
						can_send_media_messages=False,
						can_send_other_messages=False,
						can_add_web_page_previews=False)
			except TelegramError as err:
				bot.send_message(chat_id=update.message.from_user.id,
						text=str(err))
				update.message.delete()
				return
			set_user_ban(userid, group, until)

	whois_msg = prepare_whois_message(userid,
			update.message.reply_to_message.from_user.username)
	update.message.delete()
	if until is not None:
		bot.send_message(chat_id=update.message.from_user.id,
				text="<b>UTENTE BANNATO</b>\n" + whois_msg +\
						"\n\n<b>FINO AL: " + datetime.datetime.fromtimestamp(until).strftime("%d/%m/%Y %H:%M") + "</b>",
						parse_mode=telegram.ParseMode.HTML)
	else:
		bot.send_message(chat_id=update.message.from_user.id,
				text="<b>UTENTE BANNATO</b>\n" + whois_msg,
				parse_mode=telegram.ParseMode.HTML)

def unban_user(bot, update, args, chat_data):
	if not args or args[0] is None or args[0] == "":
		if update.message.reply_to_message is not None:
			userid = update.message.reply_to_message.from_user.id
			username = update.message.reply_to_message.from_user.username
		else:
			return
	else:
		try:
			userid = int(args[0])
		except ValueError:
			bot.send_message(chat_id=update.message.from_user.id,
					text="L'argomento passato non è un intero!")
			update.message.delete()
			return

		if userid is not None and userid != 0:
			try:
				username = bot.get_chat_member(
						chat_id=update.message.chat_id,
						user_id=userid).user.username
			except TelegramError as err:
				bot.send_message(chat_id=update.message.from_user.id,
						text=str(err))
				update.message.delete()
				return
	if userid is None or userid == 0:
		return
	infos = None
	if username is not None and username != "":
		infos = get_user_info(username)

	if 'spammers' in chat_data:
		if userid in chat_data['spammers']:
			chat_data['spammers'].remove(userid)

	try:
		if infos is not None:
			bot.restrict_chat_member(chat_id=update.message.chat_id,
					user_id=userid,
					can_send_messages=True,
					can_send_media_messages=True,
					can_send_other_messages=True,
					can_add_web_page_previews=True)
		else:
			bot.restrict_chat_member(chat_id=update.message.chat_id,
					user_id=userid,
					can_send_messages=True,
					can_send_media_messages=False,
					can_send_other_messages=False,
					can_add_web_page_previews=False)
	except TelegramError as err:
		bot.send_message(chat_id=update.message.from_user.id,
				text=str(err))
	else:
		remove_user_ban(userid, update.message.chat_id)
		bot.send_message(chat_id=update.message.from_user.id,
				text="Ban rimosso!")
	finally:
		update.message.delete()



def ping(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="pong",
			reply_to_message_id=update.message.message_id)

def remove_keyboard(bot, update):
	bot.send_message(chat_id=update.message.chat_id,
			text="Rimozione custom keyboard...",
			reply_markup=telegram.ReplyKeyboardRemove())

def restart(bot, update):
	close_db_connection()
	bot.send_message(chat_id=update.message.chat_id,
			text="Bot is restarting...")
	logger.info("Bot is restarting... (requested by %s)" %
			update.message.from_user.username)
	os.remove(PID_FILE)
	time.sleep(0.2)
	os.execl(sys.executable, sys.executable, *sys.argv)

def force_collect(bot, update):
	bot.send_message(chat_id=update.message.chat_id,
			text="Collecting old memoized data...")
	memoized_collect(collect_time=0)

#def purge(bot, update):
#	bot.send_message(chat_id=update.message.chat_id,
#			text="Purging cache...")
#	logger.info("Purging cache... (requested by %s)" %
#			update.message.from_user.username)
#	memoized().purge()

def kdb_action(bot, update):
	if update.message.text == u"☑️ Verifica Account":
		show_verify_info(bot, update)
	elif update.message.text == u"👤 Info su di me":
		whoami(bot, update)

__all__ = ["show_help", "whoami", "whois", "ban_user", "unban_user", "ping",
		"remove_keyboard", "restart", "force_collect", "kdb_action"]
