<?php

// ********************************
// 
// This script will try to figure out the best locale to use.
// If no locale is already specified, and an appropriate locale is found, 
// it will load the index.html file with that locale. All get parameters
// will also be forwarded.
//
// ********************************



// This function would be particularly useful, but it seems to be available only on PHP5+
//$locale = locale_accept_from_http($_SERVER['HTTP_ACCEPT_LANGUAGE']);

// Array of supported languages. In lower case.
$supported_languages = array( 
    "es" => 1,  
    "en" => 1,
    "eu" => 1
); 

// Default language.
$default_language = "en"; 

// Find out which language to use.
function negotiate_language() { 
    global $supported_languages;

    /* If the client has sent an Accept-Language: header, 
     * see if it is for a language we support. 
     */ 
    if ($_SERVER["HTTP_ACCEPT_LANGUAGE"]) { 
        $accepted = explode( ",", $_SERVER["HTTP_ACCEPT_LANGUAGE"]); 
        for ($i = 0; $i < count($accepted); $i++) { 
            $lang = strtolower(substr($accepted[$i], 0, 2));
            if ($supported_languages[$lang]) { 
                return $accepted[$i]; 
            } 
        } 
    } 

    /* Check for a valid language code in the 
     * top-level domain of the client's source address. 
     */ 
    if (eregi( "\\.[^\\.]+$", $REMOTE_HOST, &$arr)) { 
        $lang = strtolower($arr[1]); 
        if ($supported_languages[$lang]) { 
            return $lang; 
        } 
    } 

    global $default_language; 
    return $default_language; 
} 

$get_params = $_GET;

// If we don't have a locale we will find the most appropriate one. If we do
// have one, we will not modify it.
if( ! $_GET['locale'] )
{
    // Get the best locale.
    $locale = negotiate_language();
    $get_params['locale'] = substr($locale, 0, 2);
}

// Now we need to rebuild the request
// without losing any GET parameter.
$get_params_str = http_build_query($get_params, null, '&');

// Redirect using the parameters we just built.
header('Location: index.html?' . $get_params_str);

?>
