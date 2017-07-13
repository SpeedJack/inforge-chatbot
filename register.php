<?php

if (isset($_POST["userid"]) && !empty($_POST["userid"])) {
	$userid = $_POST["userid"];
} else {
	echo "NO-ID";
	exit;
}
if (isset($_POST["username"]) && !empty($_POST["username"])) {
	$username = $_POST["username"];
} else {
	echo "NO-NAME";
	exit;
}
if (isset($_POST["telegram"]) && !empty($_POST["telegram"])) {
	$telegram = $_POST["telegram"];
} else {
	$telegram = "";
}
if (isset($_POST["signature"]) && !empty($_POST["signature"])) {
	$signature = $_POST["signature"];
} else {
	echo "NO-SIG";
	exit;
}

$secret = "***REMOVED***";
$real_signature = md5($userid . $username . $telegram . $secret);
if ($signature != $real_signature) {
	echo "INVALID-SIG";
	exit;
}

$db = new SQLite3("/home/ovh/chatbot/chatbot.db");
if (!$db) {
	echo "DB-ERR";
	exit;
}

if ($telegram == "") {
	$stmt = $db->prepare("DELETE FROM users WHERE ifuserid = :uid");
	$stmt->bindValue(":uid", $username, SQLITE3_INTEGER);
	$result = $stmt->execute();
	echo "OK";
	$db->close();
	exit;
}
$stmt = $db->prepare("SELECT COUNT(*) AS num FROM users WHERE tgusername = :tg AND ifuserid != :uid");
$stmt->bindValue(":tg", $telegram, SQLITE3_TEXT);
$stmt->bindValue(":uid", $username, SQLITE3_INTEGER);
$result = $stmt->execute();
$arr = $result->fetchArray();
if ($arr === false || $arr['num'] > 0) {
	echo "DUP";
} else {
	$stmt = $db->prepare("INSERT OR REPLACE INTO users(ifuserid, ifusername, tgusername, restricted) VALUES (:uid, :name, :tg, 1)");
	$stmt->bindValue(":uid", $userid, SQLITE3_INTEGER);
	$stmt->bindValue(":name", $username, SQLITE3_TEXT);
	$stmt->bindValue(":tg", $telegram, SQLITE3_TEXT);
	$stmt->execute();
	echo "OK";
}
$db->close();
