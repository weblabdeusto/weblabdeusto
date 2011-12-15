<?php

/* 
 Copyright (C) 2011 onwards University of Deusto
 All rights reserved.

 This software is licensed as described in the file COPYING, which
 you should have received as part of this distribution.

 This software consists of contributions made by many individuals, 
 listed below:

 Author: Pablo Orduña <pablo@ordunya.com>
*/

require("WebLabHttpRequestGateway.class.php");
require("WebLabData.class.php");

class WebLabDeusto
{

    public function __construct($baseurl, $gateway_name = "", $cookiefile = "cookiefile")
    {
        $this->baseurl = $baseurl;

        // Set the default gateway
        if($gateway_name == "")
            $gateway_name = WebLabHttpRequestGateway::$HTTPCLIENT;

        $this->gateway_name = $gateway_name;

        if($gateway_name == WebLabHttpRequestGateway::$CURL)
            $this->gateway  = new CurlHttpRequestGateway($baseurl, $cookiefile);
        else if($gateway_name == WebLabHttpRequestGateway::$HTTPCLIENT)
            $this->gateway  = new HttpClientHttpRequestGateway($baseurl, $cookiefile);
        else
            die('Unsupported weblab http gateway: ' . $gateway_name);
    }

    public function getGatewayName()
    {
        return $this->gateway_name;
    }

    private function serialize_request($method, $params)
    {
        $request_data = array( 
                    "method"  => $method,
                    "params"  => $params
                );
        return json_encode($request_data);
    }

    private function login_call($serialized_request)
    {
        $serialized_response = $this->gateway->login_call($serialized_request);       
        return json_decode($serialized_response, TRUE);
    }

    private function core_call($method, $params)
    {
        $serialized_request = $this->serialize_request($method, $params);
        $serialized_response = $this->gateway->core_call($serialized_request);
        return json_decode($serialized_response, TRUE);
    }

    public function login( $username, $password )
    {
        $serialized_request = $this->serialize_request("login", array(
                        "username" => $username,
                        "password" => $password
                    ));
        $response_data = $this->login_call($serialized_request);

        if(!$response_data['is_exception'])
        {
            return $response_data['result']['id'];
        }
        else
        {
            die("ERROR: " . $response_data['message'] . "\n");
        }
    }

    public function reserve( $session_id, $exp_name, $exp_category, $initial_data = "{}", $consumer_data = array() )
    {
        $response_data = $this->core_call("reserve_experiment", array(
                        "session_id" => array(
                            "id" => $session_id,
                        ),
                        "experiment_id" => array(
                            "exp_name" => $exp_name,
                            "cat_name" => $exp_category
                        ),
                        "client_initial_data" => $initial_data,
                        "consumer_data" => json_encode($consumer_data)
                    ));

        if(!$response_data['is_exception'])
        {
            return Reservation::create($response_data['result']);
        }
        else
        {
            die("ERROR: " . $response_data['message'] . "\n");
        }
    }

    public function get_reservation_status( $reservation_id )
    {
        $response_data = $this->core_call("get_reservation_status", array(
                        "reservation_id" => array(
                            "id" => $reservation_id,
                        )));

        if(!$response_data['is_exception'])
        {
            return Reservation::create($response_data['result']);
        }
        else
        {
            die("ERROR: " . $response_data['message'] . "\n");
        }
    }

    public function list_experiments( $session_id )
    {
        $response_data = $this->core_call("list_experiments", array(
                        "session_id" => array(
                            "id" => $session_id,
                        ),
                    ));

        if(!$response_data['is_exception'])
        {
            $response = array();
            foreach($response_data['result'] as $pos => $experiment)
            {
                $response[$pos] = new ExperimentPermission(
                    $experiment['experiment']['name'],
                    $experiment['experiment']['category']['name'],
                    $experiment['time_allowed']
                );
            }
            return $response;
        }else
        {
            die("ERROR: " . $response_data['message'] . "\n");
        }
    }

    public function create_client($reservation_status)
    {
        return $this->baseurl . "client/federated.html#reservation_id=" . $reservation_status->reservation_id;
    }
}

?>
