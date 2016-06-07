<?php 
    /**
    * 
    *  This PHP file populates the database 'WebLabPHPSessions', so the rest of the
    *  PHP application can focus on developing the remote laboratory. So as to use it,
    *  populate the database with the "initial.sql" file.
    * 
    */
    include "config.php";

    if (array_key_exists('PATH_INFO', $_SERVER)) {
        $path_info = $_SERVER['PATH_INFO'];

        if (strpos($path_info, '/weblab/sessions/') === 0) {

            $mysqli = new mysqli("localhost", $USERNAME, $PASSWORD, $DB);

            if ($_SERVER['REQUEST_METHOD'] == 'POST' && $path_info == '/weblab/sessions/') {
                $postdata = file_get_contents("php://input");
                $weblab_data = json_decode($postdata, TRUE);

                // weblab_data is a array such as:
                // array(
                //    'client_initial_data' => {},
                //    'server_initial_data' => { "priority.queue.slot.start" : "2013-05-01 08:30:40.123", "priority.queue.slot.length" : "200", "request.username" : "porduna"  },
                //    'back' => 'http://www.weblab.deusto.es/.../'
                // );

                $server_initial_data = $weblab_data['server_initial_data'];

                $username = $server_initial_data["request.username"];
                    
                $back = $weblab_data['back'];

                // A bad way to make a random number
                $session_id = uniqid("", TRUE);

                // Watch SQL injection!
                $mysqli->query("INSERT INTO WebLabSessions(session_id, back, last_poll, max_date, username) VALUES('" . $session_id . "', '" . $back . "', NULL, NULL, '" . $username . "')");

                echo json_encode(array("session_id" => $session_id, "url" => "http://localhost/phplab/index.php?session_id=" . $session_id));

            } else if (strpos($path_info, '/weblab/sessions/api') === 0) {

                echo json_encode(array('api_version' => "1"));

            } else if (strpos($path_info, '/weblab/sessions/test') === 0) {

                echo json_encode(array('valid' => true));

            } else if (strpos($path_info, '/weblab/sessions/') === 0 && strpos($path_info, '/status') > 0) {
                $session_id = substr($path_info, strlen('/weblab/sessions/'), -strlen('/status'));

                echo json_encode(array('should_finish' => 10));
            } else if ($_SERVER['REQUEST_METHOD'] == 'POST' && strpos($path_info, '/weblab/sessions/') === 0) {

                $session_id = substr($path_info, strlen('/weblab/sessions/'));


                $postdata = file_get_contents("php://input");
                $weblab_data = json_decode($postdata, TRUE);
               
                if ($weblab_data["action"] == "delete") {
                    $result = $mysqli->query("SELECT back FROM WebLabSessions WHERE session_id = '" . $session_id . "'");
                    if ($result->num_rows > 0) {

                        $back = $result->fetch_assoc()['back'];

                        // Watch SQL injection!
                        $mysqli->query("INSERT INTO WebLabExpiredSessions(session_id, back, expired) VALUES('" . $session_id . "', '" . $back . "', NULL)");
                        $mysqli->query("DELETE FROM WebLabSessions WHERE session_id = '" . $session_id . "'");
                        echo "deleted";
                    } else {
                        echo "not found";
                    }
                }

            } else {
                ?>
                Invalid WebLab-Deusto address.
                <?php
            }

            mysqli_close($mysqli);

            exit(0);
        }
    } 
?>

Invalid address. It should start by /weblab/sessions/something


