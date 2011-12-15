<?php

require("weblabdeusto.class.php");

////////////////////
// 
// Usage sample
// We log in:
// 

// Default (HTTPCLIENT)
$weblab = new WebLabDeusto("http://localhost/weblab/");

// Using HttpClient: instance-level cookies; no support for HTTPS
// $weblab = new WebLabDeusto("http://localhost/weblab/", WebLabHttpRequestGateway::$HTTPCLIENT);
// 
// Using CURL: support for HTTPS; cookies stored in file: common to 
// all requests. If the login cookie expires while another request 
// is in process, this request fails
// $weblab = new WebLabDeusto("http://localhost/weblab/", WebLabHttpRequestGateway::$CURL); // additional optional argument: cookiefile

// Using CURL with different cookie file
// $weblab = new WebLabDeusto("http://localhost/weblab/", WebLabHttpRequestGateway::$CURL, "cookiefile");

echo "Using http gateway: " . $weblab->getGatewayName() . "<br/>\n";

$sess_id = $weblab->login("any","password");

//////////////////////////////////////////////
//
// Ask for the available experiments (with session_id)
// (see "ExperimentPermission")
// 

$experiments = $weblab->list_experiments($sess_id);
foreach($experiments as $experiment)
    echo "I have permission " . $experiment->name . " of category " . $experiment->category . " during " . $experiment->assigned_time . " seconds <br/>\n";

////////////////////////////////////////
// 
// Create reservation (still with session_id)
//

$exp_name = "ud-dummy";
$cat_name = "Dummy experiments";

$consumer_data = array(

// 
// Consumer data is an optional argument that can be used to ask the weblab
// server to store different information rather than the one it can try to
// get. For instance, if this PHP software is a not-traditional consumer
// which proxies other users (as running in Moodle), WebLab-Deusto will 
// store the PHP library user-agent rather than the actual final user 
// user-agent. If this component knew what is the actual user agent, it should
// provide it. Same applies to other fields (such as from_ip, etc.)
// 

//    "user_agent"    => $_SERVER['HTTP_USER_AGENT'],
//    "referer"       => $_SERVER['HTTP_REFERER'],
//    "from_ip"       => $_SERVER['REMOTE_ADDR'],

// 
// Additionally, the consumerData may be used to provide scheduling arguments,
// or to provide a user identifier (that could be an anonymized hash).
// 

    "external_user"                 => "moodle_student1",
//    "priority"                      => 3, // the lower, the better
//    "time_allowed"]                 => 100, // seconds
//    "initialization_in_accounting"] => false,
);

$reservation_status = $weblab->reserve($sess_id, $exp_name, $cat_name,"{}", $consumer_data);
var_dump($reservation_status);

// Optional: check the reservation (now with reservation_id)

$reservation_status = $weblab->get_reservation_status($reservation_status->reservation_id);
var_dump($reservation_status);

$client_url = $weblab->create_client($reservation_status);

echo  "URL: " . $client_url . "\n";

echo "<br/><br/><a href=\"" . $client_url . "\">open</a>";

?>
