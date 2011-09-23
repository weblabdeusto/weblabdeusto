<?php

/* September 2011 - Pablo Orduña <pablo.orduna@deusto.es>
*/

class ExperimentPermission
{
    public function __construct($name, $category, $assigned_time)
    {
        $this->name     = $name;
        $this->category = $category;
        $this->assigned_time = $assigned_time;
    }
}

// 
// Abstract class: use create() method
// For further information, take a look at:
// 
// http://code.google.com/p/weblabdeusto/source/browse/server/src/weblab/core/reservations.py
// 
abstract class Reservation
{
    public function __construct($reservation_id, $status)
    {
        $this->reservation_id = $reservation_id;
        $this->status         = $status;
    }

    public static function create($data_structure)
    {
        $reservation_id = $data_structure['reservation_id']['id'];
        if($data_structure['status'] == 'Reservation::waiting_confirmation')
            return new WaitingConfirmationReservation($reservation_id);
        else if($data_structure['status'] == 'Reservation::waiting')
            return new WaitingReservation($reservation_id, $data_structure['position']);
        else if($data_structure['status'] == 'Reservation::waiting_instances')
            return new WaitingInstancesReservation($reservation_id, $data_structure['position']);
        else if($data_structure['status'] == 'Reservation::confirmed')
            return new ConfirmedReservation($reservation_id, $data_structure['time'], $data_structure['initial_configuration']);
        else if($data_structure['status'] == 'Reservation::post_reservation')
            return new PostReservationReservation($reservation_id, $data_structure['finished'], $data_structure['initial_data'], $data_structure['end_data']);
        else
            die("Unexpected reservation: " . $data_structure);
    }
}

class WaitingConfirmationReservation extends Reservation
{
    public function __construct($reservation_id)
    {
        parent::__construct($reservation_id, 'waiting_confirmation');
    }
}

class WaitingReservation extends Reservation
{
    public function __construct($reservation_id, $position)
    {
        parent::__construct($reservation_id, 'waiting');
        $this->position = $position;
    }
}

class WaitingInstancesReservation extends Reservation
{
    public function __construct($reservation_id, $position)
    {
        parent::__construct($reservation_id, 'waiting_instances');
        $this->position = $position;
    }   
}

class ConfirmedReservation extends Reservation
{
    public function __construct($reservation_id, $time, $initial_configuration)
    {
        parent::__construct($reservation_id, 'confirmed');
        $this->time                  = $time;
        $this->initial_configuration = $initial_configuration;
    }   
}

class PostReservationReservation extends Reservation
{    
    public function __construct($reservation_id, $finished, $initial_data, $end_data)
    {
        parent::__construct($reservation_id, 'post_reservation');
        $this->finished     = $finished;
        $this->initial_data = $initial_data;
        $this->end_data     = $end_data;
    }
}

class WebLabDeusto
{

    public function __construct($hostname, $cookiefile = "cookiefile")
    {
        $this->hostname = $hostname;
        $this->cookiefile = $cookiefile;
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
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_COOKIESESSION, 1);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $this->cookiefile);
        curl_setopt($ch, CURLOPT_COOKIEJAR, $this->cookiefile);

        curl_setopt($ch, CURLOPT_URL, $this->hostname . "login/json/");
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $serialized_request);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

        $serialized_response = curl_exec($ch);
       
        return json_decode($serialized_response, TRUE);
    }

    private function core_call($method, $params)
    {
        $serialized_request = $this->serialize_request($method, $params);
        
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_COOKIESESSION, 1);
        curl_setopt($ch, CURLOPT_COOKIEFILE, "cookiefile");
        curl_setopt($ch, CURLOPT_COOKIEJAR, "cookiefile");

        curl_setopt($ch, CURLOPT_URL, $this->hostname . "json/");
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $serialized_request);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

        $serialized_response = curl_exec($ch);
        
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

    public function reserve( $session_id, $exp_name, $exp_category, $initial_data )
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
                        "consumer_data" => "{}"
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

    public function create_client($reservation_status, $exp_name, $cat_name)
    {
        return $this->hostname . "client/federated.html#reservation_id=" . $reservation_status->reservation_id;
    }
}

?>
