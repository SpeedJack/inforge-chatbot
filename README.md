# Inforge Chatbot
Old inforge Chatbot code. No longer maintained.

## Installazione
Clonare il repository:  
```
$ git clone https://github.com/InforgeNet/inforge-chatbot.git --recursive
```
Installare le dipendenze:  
```
$ cd modules/python-telegram-bot
As root:
# python setup.py install
```
## Avviare
Configurazione:  
```
$ ./create-db.sh
$ vim config.py
```
Avvio per prova del solo bot:  
```
$ ./chatbot.py
```
Avvio completo (assicurarsi che bot token e tutto il resto sia correttamente modificato anche in bot-controller.sh, non solo in config.py):  
```
$ ./stop.sh
$ cronjob -e
55 4 * * * cd /path/to/repo && ./backup.sh
* * * * * cd /path/to/repo && ./bot-controller.sh
30 3 */7 * * truncate -s 0 /home/ovh/chatbot/chatbot.log
(Salva e chiudi)
$ ./start.sh
```
## Aggiornamento
```
$ git pull
$ git submodule update --recursive
$ cd modules/python-telegram-bot
# python setup.py install
```
## Log file
Potete scaricare l'attuale log file dal VPS andando al seguente link:
```
https://telegram.inforge.net/tgbot/log-viewer.php?key=***REMOVED***
```
## Database
Potete eseguire query sul database andando al seguente link:
```
https://telegram.inforge.net/tgbot/run-query.php?key=***REMOVED***
```
Eseguite solo query di SELECT; chi fa danni ne paga le conseguenze.
