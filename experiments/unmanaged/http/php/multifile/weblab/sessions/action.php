<?php
    include "config.php";
    
    check_from_weblab();

    $mysqli = new mysqli("localhost", $USERNAME, $PASSWORD, $DB);

    $session_id = $_GET["session_id"];


    if ($_POST["action"] == "delete") {
        $result = $mysqli->query("SELECT back FROM WebLabSessions WHERE session_id = '" . $session_id . "'");
        if ($result->num_rows > 0) {

            $back = $result->fetch_assoc()['back'];

            // Watch SQL injection!
            $mysqli->query("INSERT INTO WebLabExpiredSessions(session_id, back, expired) VALUES('" . $session_id . "', '" . $back . "', NULL)");
            $mysqli->query("DELETE FROM WebLabSessions WHERE session_id = '" . $session_id . "'");
            echo json_encode(array("message" => "deleted"));
        } else {
            echo json_encode(array("message" => "not found"));
        }
    } else {
        echo json_encode(array("message" => "unknown action"));
    }

    mysqli_close($mysqli);
