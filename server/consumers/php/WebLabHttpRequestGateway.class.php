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

abstract class WlHttpRequestGateway
{
    abstract public function login_call($serialized_request);
    abstract public function core_call($serialized_request);
}

class CurlHttpRequestGateway extends WlHttpRequestGateway
{
    public function __construct($baseurl, $cookiefile)
    {
        $this->baseurl   = $baseurl;
        $this->cookiefile = $cookiefile;
    }

    public function login_call($serialized_request)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_COOKIESESSION, 1);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $this->cookiefile);
        curl_setopt($ch, CURLOPT_COOKIEJAR, $this->cookiefile);

        curl_setopt($ch, CURLOPT_URL, $this->baseurl . "login/json/");
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $serialized_request);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

        $serialized_response = curl_exec($ch);
        return $serialized_response;
    }

    public function core_call($serialized_request)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_COOKIESESSION, 1);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $this->cookiefile);
        curl_setopt($ch, CURLOPT_COOKIEJAR, $this->cookiefile);

        curl_setopt($ch, CURLOPT_URL, $this->baseurl . "json/");
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $serialized_request);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

        $serialized_response = curl_exec($ch);
        return $serialized_response;
    }
}

class HttpClientHttpRequestGateway extends WlHttpRequestGateway
{
    public function __construct($baseurl)
    {
        require("lib/HttpClient.class.php");

        $url_tokens = explode("/", $baseurl);
        $this->domain   = $url_tokens[2];
        $url_tokens = explode($this->domain, $baseurl);
        $this->location = $url_tokens[1];
        $this->cookies  = array();
    }

    public function login_call($serialized_request)
    {
        $client = new HttpClient($this->domain);
        $client->post($this->location . "login/json/", $serialized_request);

        $content = $client->getContent();

        $this->cookies = $client->getCookies();

        var_dump($this->cookies);

        return $content;
    }

    public function core_call($serialized_request)
    {
        $client = new HttpClient($this->domain);
        $client->setCookies($this->cookies);
        $client->post($this->location . "json/", $serialized_request);

        return $client->getContent();
    }
}
?>
