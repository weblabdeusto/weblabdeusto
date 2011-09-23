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

?>
