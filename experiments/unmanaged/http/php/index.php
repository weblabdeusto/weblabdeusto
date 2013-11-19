<?php

include "config.php";

if (array_key_exists("session_id", $_GET)) {

    $mysqli = new mysqli("localhost", $USERNAME, $PASSWORD, $DB);

    $result = $mysqli->query("SELECT username FROM WebLabSessions WHERE session_id = '" . $_GET["session_id"] . "'");
    if($result->num_rows > 0) {
        $username = $result->fetch_assoc()['username'];
        echo "Hi there, " . $username;
    } else {
        $result = $mysqli->query("SELECT back FROM WebLabExpiredSessions WHERE session_id = '" . $_GET["session_id"] . "'");
        if ($result->num_rows > 0) {
            $back = $result->fetch_assoc()['back'];
            echo "Hi. I'm sorry. Your time has passed. Go <a href='" . $back . "'>back</a>";
        } else {
            echo "You're not logged in.";
        }
    }

    mysqli_close($mysqli);

} else {
?>

Warning: session_id not available.

<?php
}

?>
