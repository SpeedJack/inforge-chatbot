# Inforge Chatbot
**ATTENZIONE:** questo è un repository privato, accessibile solo allo Staff di inforge.net  

Il codice sorgente di questo bot contiene _informazioni pericolose_ se rilasciate al pubblico (tra cui, _token_ del bot di inforge e _API key_ del forum di inforge: vuol dire che se qualcuno entra in possesso del codice contenuto in questo repository può: 1) _bannare_ tutti gli utenti nella chat Telegram; 2) _danneggiare_ direttamente il forum, eliminando contenuti, bannando utenti, ecc.). **Se qualcuno verrà sorpreso a condividere parti del codice di questo bot senza autorizzazione sarà immediatamente espulso dallo Staff e allontanato dalla community e sarà ritenuto direttamente responsabile di qualsiasi danno causato a inforge.net e ai servizi collegati.** _È altresì vietato utilizzare l'API key di inforge o il token del bot senza autorizzazione di un amministratore._ Se dovete fare dei test o provare il codice, potete creare il vostro bot con il vostro token con @BotFather. Prima di fare dei test, assicuratevi di aver correttamente cambiato il bot token sia in config.py sia in bot-controller.sh (se testate quest'ultimo).  

Se pensate di poter migliorare il codice, potete effettuare modifiche. **Non forkate il repository!**. Se forkate il repository, la vostra fork diventa pubblica e accessibile a tutti (a meno che non pagate per repo privati). Per fare modifiche, _create una nuova branch_ e pushate in quella branch. Se poi le riterrò valide, provvederò a fare il merge con la branch master. Alternativamente potete anche creare delle _patch_ con _diff_ e mandarmele in privato.  

_-- SpeedJack_  

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
