<?php
    include "config.php";

    check_from_weblab();

    $mysqli = new mysqli("localhost", $USERNAME, $PASSWORD, $DB);

    // $_POST is a array such as:
    // array(
    //    'client_initial_data' => {},
    //    'server_initial_data' => { "priority.queue.slot.start" : "2013-05-01 08:30:40.123", "priority.queue.slot.length" : "200", "request.username" : "porduna"  },
    //    'back' => 'http://www.weblab.deusto.es/.../'
    // );

    $server_initial_data = json_decode($_POST['server_initial_data'], TRUE);

    $username = $server_initial_data["request.username"];
        
    $back = $_POST['back'];

    // A bad way to make a random number
    $session_id = uniqid("", TRUE);

    // Watch SQL injection!
    $mysqli->query("INSERT INTO WebLabSessions(session_id, back, last_poll, max_date, username) VALUES('" . $session_id . "', '" . $back . "', NULL, NULL, '" . $username . "')");

    echo json_encode(array("session_id" => $session_id, "url" => "http://localhost/phplab/index.php?session_id=" . $session_id));

    mysqli_close($mysqli);

