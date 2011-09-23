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

abstract class WebLabHttpRequestGateway
{
    public static $CURL       = 'WEBLABDEUSTO_GATEWAY_CURL';
    public static $HTTPCLIENT = 'WEBLABDEUSTO_GATEWAY_HTTPCLIENT';

    abstract public function login_call($serialized_request);
    abstract public function core_call($serialized_request);
}

class CurlHttpRequestGateway extends WebLabHttpRequestGateway
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

        return curl_exec($ch);
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

        return curl_exec($ch);
    }
}

class HttpClientHttpRequestGateway extends WebLabHttpRequestGateway
{

    public function __construct($baseurl)
    {
        require_once("lib/HttpClient.class.php");

        $url_tokens = explode("/", $baseurl);
        $this->domain   = $url_tokens[2];
        $url_tokens = explode($this->domain, $baseurl);
        $this->location = $url_tokens[1];
        $this->cookies  = array();
    }

    public function login_call($serialized_request)
    {
        $client = new HttpClient($this->domain);
        $client->cookie_host = $this->domain;
        $client->post($this->location . "login/json/", $serialized_request);

        $this->cookies = $client->getCookies();
        return $client->getContent();
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
