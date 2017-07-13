#!/usr/bin/env python

import time
import telegram
from telegram.error import TelegramError

_kbd = [[telegram.KeyboardButton(text=u"☑️ Verifica Account")],
	[telegram.KeyboardButton(text=u"👤 Info su di me")]]
_rkm = telegram.ReplyKeyboardMarkup(_kbd)

def contact(bot, userid):
	print("Contacting:", userid)
	try:
		bot.send_message(chat_id=userid,
				text="Il tuo account Telegram è stato dissociato da inforge in quanto l'username inserito sul tuo account Inforge risulta diverso dal tuo username Telegram. Pertanto non potrai inviare messaggi multimediali nel gruppo finché non completerai nuovamente la verifica dell'account. Ricorda di rispettare anche maiuscole e minuscole nel campo Telegram del tuo profilo inforge! In caso di problemi, contatta il Supporto Ticket.",
				reply_markup=_rkm)
	except TelegramError as err:
		print("Error:", str(err))

if __name__ == "__main__":
	bot = telegram.Bot(token="***REMOVED***")
	with open("to-contact.lst", "r") as f:
		for line in f:
			contact(bot, int(line.rstrip("\n")))
			time.sleep(1)
