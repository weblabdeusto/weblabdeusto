<?php

/* This file contains some contributed curl utilities. 
 * With curl, you can make https (ssl/tls) requests.
 *
 * These require that you have the php curl extension
 * properly installed.
 *
 * I have not tested these personally, but am told that they
 * work. ymmv.
 *
 * and thank-you to the [anonymous] submitter of these routines!
 */


/* xu_rpc_http_curl() -- Call xmlrpc method on a remote http server
 *                       using CURL Library.
 *
 *  $txtMethod  - name of remote method to call (required).
 *  $arrayArgs  - Args to remote call (required).
 *  $txtURL     - remote url (required).
 *  $boolSecure - Use OpenSSL for encryption.
 *  $boolDebug  - Debuging
 *  $objOutput  - see output arg to xu_rpc_http in utils.php
 */
function xu_rpc_http_curl( $txtMethod, $arrayArgs, $txtURL,
                           $boolSecure=false, $boolDebug=false,
                           $objOutput) {
   if (!$objOutput) {
      $objOutput = array(version => 'xmlrpc');
   }

   /*
   ** we assume a fully qualified URL
   **      https?://host.name.com:port/URI_PATH
   ** (automatic for xu_rpc_http_curl_compat2)
   */
   $arrayParts = split('/', $txtURL);

   $txtHost = $arrayParts[2];
   $intPort = 80;

   if ( strstr( $txtHost, ':') ) {
      list($txtHost, $intPort) = split(':', $txtHost);
   }

   /*
   ** strip off transport:, and blank array element and host:port
   */
   array_shift($arrayParts);
   array_shift($arrayParts);
   array_shift($arrayParts);

   $txtURI = '/' . join('/', $arrayParts);

   return xu_rpc_http_concise_curl(array('txtMethod'  => $txtMethod,
                                         'arrayArgs'  => $arrayArgs,
                                         'txtURL'     => $txtURL,
                                         'txtHost'    => $txtHost,
                                         'intPort'    => $intPort,
                                         'txtURI'     => $txtURI,
                                         'boolSecure' => $boolSecure,
                                         'boolDebug'  => $boolDebug,
                                         'objOutput'  => $objOutput));
}


/* xu_rpc_http_concise_curl() -- Call xmlrpc method on a remote
 *                               http server using CURL Library.
 *
 * $arrayParam  - Associative array (struct) holding options:
 *   txtMethod  - name of method to call (required).
 *   arrayArgs  - Parameters to remote xmlrpc server (required).
 *   txtURL     - remote url (required).
 *   txtHost    - remote host (required).
 *   txtURI     - remote uri (required).
 *   intPort    - remote port (required).
 *   boolSecure - [false] true for OpenSSL for encryption.
 *   boolDebug  - [false] debuging.
 *   $objOutput  - see output arg to xu_rpc_http in utils.php
 */
function xu_rpc_http_concise_curl($arrayParam) {

   // 1) set up variables and verify.
   extract($arrayParam);

   if (!isset($boolSecure)) {
      $boolSecure = false;
   }

   if (!isset($boolDebug)) {
      $boolDebug = false;
   }

   if (!isset($objOutput)) {
      $objOutput = array(version => "xmlrpc");
   }

   if ((isset($txtMethod)) and (isset($txtURL) ) and
   (isset($txtHost)  ) and (isset($intPort)) and
   (isset($txtURI)   )) {

      // 2) xmlrpc encode request.
      $txtRequest = xmlrpc_encode_request($txtMethod, $arrayArgs, $objOutput);

      $intContentLen = strlen($txtRequest);

      dbg1("opening curl to $txtURL", $boolDebug);

      $txtTransport = 'HTTPS';
      if ($boolSecure) {
         $txtTransport = 'HTTPS';
      }

      $txtHTTP_Request =
      "POST $txtURI $txtTransport/1.0\r\n" .
      "User-Agent: xmlrpc-epi-php/0.2 (PHP) \r\n" .
      "Content-Type: text/xml\r\n" .
      "Content-Length: $intContentLen\r\n" .
      "\r\n" .
      "$txtRequest";

      dbg1( "sending http request:</h3> <xmp>\n$txtHTTP_Request\n</xmp>",$boolDebug);

      
      // 3) open CURL, and send data.
      $objCURL = curl_init($txtURL);

      curl_setopt($objCURL, CURLOPT_RETURNTRANSFER, 1);
      curl_setopt($objCURL, CURLOPT_CUSTOMREQUEST, $txtHTTP_Request);
      curl_setopt($objCURL, CURLOPT_HEADER, 0);

      if ($a_boolSecure) {
         curl_setop($objCURL, CURLOPT_SSLVERSION, 3);
      }

      
      //  4) read response, and close CURL.
      $txtResponse = curl_exec($objCURL);

      curl_close($objCURL);

      dbg1( "got response:</h3>. <xmp>\n$txtResponse\n</xmp>\n",
      $boolDebug);

      
      //  5) xmlrpc decode result.
      $objReturn = find_and_decode_xml($txtResponse, $boolDebug);
   }

   
   //  6) return result.
   return $objReturn;
}


/*  xu_rpc_http_curl_compat() - Calls xu_rpc_http_curl with almost
 *                               the same args as xu_rpc_http for easy
 *                               conversion of scripts. [doesn't include
 *                               $timeout, $user, or $pass].
 *
 *   $txtMethod  - Method to call on remote xmlrpc server (required).
 *   $arrayArgs  - Args to remote call (required).
 *   $txtHost    - Host to connect to (required).
 *   $txtURI     - ['/'] remote path to server.
 *   $intPort    - [80] remote server port.
 *   $boolDebug  -       [false] true turns on debug.
 *   $boolSecure - [false] true means use https request with CURL for
 *                 SSL encryption.
 *   $objOutput  - see output arg to xu_rpc_http in utils.php
 */
function xu_rpc_http_curl_compat($txtMethod, $arrayArgs, $txtHost, 
                                 $txtURI='/', $intPort=80, 
                                 $boolDebug=false, $boolSecure=false,
                                 $objOutput) {
   if ($objOutput) {
      $objOutput = array(version => 'xmlrpc');
   }

   $txtTransport = $boolSecure ? 'https://' : 'http://';

   $txtURL = "$txtTransport$txtHost:$intPort$txtURI";

   return xu_rpc_http_curl( $txtMethod, $arrayArgs, $txtURL,
                            $boolSecure, $boolDebug, $objOutput);
}


?>
