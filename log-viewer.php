<?php
if ($_GET['key'] !== "***REMOVED***") {
	exit
}

header("Content-Type: application/octet-stream");
header("Content-Disposition: attachment; filename=chatbot.log");
readfile("/home/ovh/chatbot/chatbot.log");
