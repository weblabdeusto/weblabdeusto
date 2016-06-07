<?php
    include "config.php";

    check_from_weblab();
    
    echo json_encode(array('should_finish' => 10));

