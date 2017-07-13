#!/usr/bin/env python3

import telegram

if __name__ == "__main__":
	bot = telegram.Bot(token="***REMOVED***")
	bot.send_message(chat_id=-1001055827794,
			text="Rimozione custom keyboard...",
			reply_markup=telegram.ReplyKeyboardRemove())
