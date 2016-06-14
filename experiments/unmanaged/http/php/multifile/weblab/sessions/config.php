<?php

$DB       = 'phplab';
$USERNAME = 'phplab';
$PASSWORD = 'phplab';

$WEBLAB_USER = "admin";
$WEBLAB_PASSWORD = "password";

function check_from_weblab($send_headers = true, $exit = true) {
    global $WEBLAB_USER, $WEBLAB_PASSWORD;

    if (isset($_SERVER['PHP_AUTH_USER']) && isset($_SERVER['PHP_AUTH_PW'])
        && $_SERVER['PHP_AUTH_USER'] == $WEBLAB_USER && $_SERVER['PHP_AUTH_PW'] == $WEBLAB_PASSWORD) {
        return true;
    }

    if ($send_headers) {
            http_response_code(401);
            header('WWW-Authenticate: Basic realm="Login Required"');
    }
    if ($exit) {
        exit(0);
    }
    return false;
}

