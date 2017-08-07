<?php
	$key = "***REMOVED***";
	$path_db = "/home/ovh/chatbot/chatbot.db";

	// Check key
	if(!isset($_GET['key']) || ($_GET['key'] != $key))
		exit();
	// Check POST
	$query = $_POST['query'];
	?>
<html>
<head>
	<title>Gestione database</title>
</head>
<body>
	<h1>Gestione database Telegram</h1>
	<p>Fate ATTENZIONE!</p>
	<br>
	<form action="<?php echo $_SERVER['PHP_SELF'] . "?key=" . $key; ?>" method="POST">
		Query: <input type="text" name="query" placeholder="Inserisci query" style="width:100%;"><br>
		<input type="submit" value="Invia">
	</form>
	<br>
	<hr>
	<?php
		if(isset($query)){
			// Handle query
			echo "<i>Executing query:" . $query."</i>";
			$db = new SQLite3($path_db);

			if(!$db) {
				echo "DB-ERR";
				exit;
			}

			$stmt = $db->prepare($query);

			$result = $stmt->execute();
			echo "<table border=1>";
			while($entry = $result->fetchArray(SQLITE3_NUM)){
				echo "<tr>";
				foreach($entry as $value){
					echo "<td>".$value."</td>";
				}
				echo "</tr>";
			}
			echo "</table>";
			$db->close();
		}
	?>
	<hr>
	<div>
		<h3>Esempi di query</h3>
		<div>
			<h4>Userid di tutti gli utenti bannati tramite bot</h4>
			<p>SELECT userid FROM members WHERE banned_until IS NOT NULL;</p>
		</div>
		<br>
		<div>
			<h4>Userid di tutti gli utenti bannati tramite bot PERMA</h4>
			<p>SELECT userid FROM members WHERE banned_until IS NOT NULL AND banned_until = 0;</p>
		</div>
		<br>
		<div>
			<h4>Userid di tutti gli utenti bannati tramite bot TEMP</h4>
			<p>SELECT userid FROM members WHERE banned_until IS NOT NULL AND banned_until != 0;</p>
		</div>
	</div>
	<br><br>
	<div>
		<h3>Strutture table</h3>
		<p>
			CREATE TABLE <b>members</b>(<br>
			<b>userid</b> INTEGER,<br>
			<b>groupid</b> INTEGER,<br>
			<b>banned_until</b> INTEGER DEFAULT NULL,<br>
			PRIMARY KEY(userid, groupid));
		</p>
		<p>
			CREATE TABLE <b>users</b>(<br>
			<b>ifuserid</b> INTEGER PRIMARY KEY,<br>
			<b>ifusername</b> VARCHAR(25) NOT NULL,<br>
			<b>tgusername</b> VARCHAR(32) UNIQUE NOT NULL COLLATE NOCASE,<br>
			<b>restricted</b> INTEGER NOT NULL DEFAULT 1);
		</p>
	</div>
</body>
</html>
