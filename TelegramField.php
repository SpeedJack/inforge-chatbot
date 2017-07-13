<?php

/* library/Callback/TelegramField.php */
class Callback_TelegramField
{
	public static function validate($field, &$value, &$error)
	{
		if (preg_match("/^[a-zA-Z][a-zA-Z0-9_]{3,30}[a-zA-Z0-9]$/", $value) === 1) {
			$url = "https://telegram.inforge.net/tgbot/register.php";
			$secret = "***REMOVED***";
			$visitor = XenForo_Visitor::getInstance();
			$userid = $visitor->getUserId();
			$username = $visitor['username'];
			$data = array(
				'userid' => $userid,
				'username' => $username,
				'telegram' => $value,
				'signature' => md5($userid . $username . $value . $secret)
			);
			$handle = curl_init();
			curl_setopt($handle, CURLOPT_URL, $url);
			curl_setopt($handle, CURLOPT_RETURNTRANSFER, true);
			curl_setopt($handle, CURLOPT_CONNECTTIMEOUT, 5);
			curl_setopt($handle, CURLOPT_TIMEOUT, 60);
			curl_setopt($handle, CURLOPT_SSL_VERIFYPEER, false);
			curl_setopt($handle, CURLOPT_SSL_VERIFYHOST, 0);
			curl_setopt($handle, CURLOPT_POST, 1);
			curl_setopt($handle, CURLOPT_POSTFIELDS, http_build_query($data));
			$res = curl_exec($handle);
			if ($res === "OK") {
				curl_close($handle);
				return true;
			} else if ($res === "DUP")
				$error = "L'username Telegram inserito è già registrato con un altro account. Contatta il Supporto Ticket.";
			else if ($res === false)
				$error = "Errore durante la registrazione dell'account Telegram. Contatta il Supporto Ticket riportando questo messaggio: \"" . curl_error($handle) . "\"";
			else
				$error = "Errore durante la registrazione dell'account Telegram. Contatta il Supporto Ticket riportando questo messaggio: \"" . var_export($res, true) . "\"";
		} else {
			$error = "Username Telegram non valido.";
		}
		curl_close($handle);
		$value = "";
		return false;
	}
}
