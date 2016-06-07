<?php
    include "config.php";

    if (!check_from_weblab(true, false)) {
        echo json_encode(array("valid"=>false,"error_messages"=>array("Invalid weblab credentials")));
    } else {
        echo json_encode(array("valid" => true));
    }
