<?php
  
  /*
    *
    * Copyright (C) 2005-2009 University of Deusto
    * All rights reserved.
    *
    * This software is licensed as described in the file COPYING, which
    * you should have received as part of this distribution.
    *
    * This software consists of contributions made by many individuals, 
    * listed below:
    *
    * Author: Luis Rodriguez Gil <luis.rodriguez@opendeusto.es>
    * 
    */
	
	/*
    * At least in Ubuntu GNU/Linux, it requires the package
    * "php5-xmlrpc" so as to avoid dynamic linking.
    */
	
	$host = "127.0.0.1";
    $uri = "/weblab/xmlrpc/";
    $port = 80;
    
	$message = "";

	// Variable names
	$USERNAME_FIELD_NAME = 'username';
	
	$ip = $_SERVER [ 'REMOTE_ADDR' ] ;
	
	// Necessary for the xu_rpc_http_concise function.
	include("php_utils/utils.php");
	
	function call_login_based_on_client_address($username, $remote_addr)
	{	
        global $host, $uri, $port;
		$result = xu_rpc_http_concise(
			array(
				'method'	=> "login_based_on_client_address",
				'args'  => array($username, $remote_addr),
				'host'  => $host,
				'uri'  => $uri,
				'port'  => $port
			)
		);
		
		return $result;
	}
	
	$username = $_POST[$USERNAME_FIELD_NAME];
	
	// Check for missing attributes.
	if(empty($username))
	{
		die('ERROR: Missing username field');
	}
	
	$result = call_login_based_on_client_address($username, $ip);
    
	
	$faultCode = NULL;
	if(is_array($result))
	{
		$faultCode = $result['faultCode'];
		$faultString = $result['faultString'];
		
		if($faultCode == 'XMLRPC:Client.Authentication')
			die('Error: Incorrect login or password');
	}
	
    $id = $result['id'];
    if(!empty($id))
        print $id;
    else die('Error: Unexpected server response.');
	
?>