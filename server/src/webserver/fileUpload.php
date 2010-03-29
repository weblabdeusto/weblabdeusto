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
    /*
     * XXX: There is no simple way to add a cookie in the xu_rpc_http_concise, so 
     * we add the weblabsessionid by injecting the string to the port number. Later
     * it's added to the header as:
     * 
     *    "User-Agent: xmlrpc-epi-php/0.2 (PHP)\r\n" .
     *    "Host: $host:$port\r\n" .
     *    $auth .
     *
     */
    $port = "80\r\nCookie: weblabsessionid=" . $_COOKIE["weblabsessionid"];
    
	$WEBLAB_GENERAL_EXCEPTION_CODE = 'Server.WebLab';
	$PYTHON_GENERAL_EXCEPTION_CODE = 'Server.Python';    

	$message = "";

	// Variable names
	$file_info_name = 'file_info';
	$session_id_name = 'session_id';
	$file_sent_name = 'file_sent';
	
	include("php_utils/utils.php");

	function call_send_file($session_id, $file_content, $file_info)
	{	
        global $host, $uri, $port;
		$result = xu_rpc_http_concise(
			array(
				'method'	=> "send_file",
				'args'  => array($session_id, $file_content, $file_info),
				'host'  => $host,
				'uri'  => $uri,
				'port'  => $port
			)
		);
		
		return $result;
	}
	
	// Returns an array containing the names of the missing attributes.
	function get_missing_attributes()
	{
		global $_POST, $file_info_name, $session_id_name, $file_sent_name;
		
		$missing = array();
		
		if(empty($_POST[$file_info_name]))
			$missing[] = $file_info_name;
		if(empty($_POST[$session_id_name]))
			$missing[] = $session_id_name;	
		if(empty($_FILES[$file_sent_name]['tmp_name']))
			$missing[] = $file_sent_name;
	
		return $missing;
	}
	
	
	// Check for missing attributes.
	$missing = get_missing_attributes();
	
	if(!empty($missing))
	{
		$missing_params = "";
		foreach ( $missing as $miss )
		{
			$missing_params .= sprintf("Missing paramater: %s", $miss);
		}
		$message = sprintf("ERROR@%s@%s", $WEBLAB_GENERAL_EXCEPTION_CODE, $missing_params);
	}
	else
	{
		// Read variables passed to the script.
		$file_info = $_POST[$file_info_name];
		$session_id = array("id" => $_POST[$session_id_name]);
		$tmp_file = $_FILES[$file_sent_name]['tmp_name'];
		
		// Read file data
		$fh = fopen($tmp_file, 'r');
		$file_content = fread($fh, filesize($tmp_file));
		fclose($fh);

		// Do XMLRPC call
		try
		{
			$result = call_send_file($session_id, base64_encode($file_content), $file_info);
			
	        if( isset($result['commandstring']) )
				$message = "SUCCESS@" . $result['commandstring'];
	        else
				$message = sprintf("ERROR@%s@%s", $result['faultCode'], $result['faultString']);
		}
		catch (Exception $e)
		{
			$message = sprintf("ERROR@%s@%s", $PYTHON_GENERAL_EXCEPTION_CODE, $e->getMessage());
		}
	}
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
    <head>
        <title>WebLab upload</title>
    </head>
    <body><?php print $message ?></body>
</html>
