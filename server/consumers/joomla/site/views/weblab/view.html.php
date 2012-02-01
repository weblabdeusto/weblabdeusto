<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted access');
 
// import Joomla view library
jimport('joomla.application.component.view');
require("components/com_weblab/lib/weblabdeusto.class.php");
 
/**
 * HTML View class for the HelloWorld Component
 */
class WebLabViewWebLab extends JView
{
	// Overwriting JView display method
	function display($tpl = null) 
	{
		$username = $this->get('UserName');
		if($_SERVER['REQUEST_METHOD'] == "POST") {
			$experiment_name = $_GET["experiment_name"];
			$category_name = $_GET["category_name"];
			$experiment_url = $this->getExperiment($username, $experiment_name, $category_name);
			header("Location: " . $experiment_url);
			return;
		}


		$experiments = $this->get('Experiments');
		#print_r($experiments);
		$this->experiments = array();
		foreach($experiments as $experiment){
			
			// $experiment_url = $this->getExperiment($username, $experiment[1], $experiment[2]);
			$first_character = "&";
			if(strpos($_SERVER["REQUEST_URI"], "?") == FALSE)
				$first_character = "?";
			$experiment_url = $_SERVER["REQUEST_URI"] . $first_character . "experiment_name=" . $experiment[1] . "&category_name=" . $experiment[2];
			array_push($this->experiments, new Experiment($experiment[0], $experiment[1], $experiment[2], $experiment_url));
		}
		#$gid = $user->gid;
		// Display the view
		parent::display($tpl);
	}

	private function getWeblabData(){
		$db = JFactory::getDBO();

                $query = 'SELECT host, user, password FROM #__weblab_config';
                $db->setQuery($query);
                $data = $db->loadRow();
		return $data;
	}

	private function getExperiment($username, $exp_name, $cat_name){
		$weblab_data = $this->getWeblabData();
		$weblab = new WebLabDeusto($weblab_data[0]);
		$sess_id = $weblab->login($weblab_data[1],$weblab_data[2]);
		$consumer_data = array(

// 
// Consumer data is an optional argument that can be used to ask the weblab
// server to store different information rather than the one it can try to
// get. For instance, if this PHP software is a not-traditional consumer
// which proxies other users (as running in Moodle), WebLab-Deusto will 
// store the PHP library user-agent rather than the actual final user 
// user-agent. If this component knew what is the actual user agent, it should
// provide it. Same applies to other fields (such as from_ip, etc.)
// 

    "user_agent"    => $_SERVER['HTTP_USER_AGENT'],
    //"referer"       => $_SERVER['HTTP_REFERER'],
    "from_ip"       => $_SERVER['REMOTE_ADDR'],

// 
// Additionally, the consumerData may be used to provide scheduling arguments,
// or to provide a user identifier (that could be an anonymized hash).
// 

    "external_user"                 => $username,
//    "priority"                      => 3, // the lower, the better
//    "time_allowed"]                 => 100, // seconds
//    "initialization_in_accounting"] => false,
);
		$reservation_status = $weblab->reserve($sess_id, $exp_name, $cat_name,"{}", $consumer_data);
		$reservation_status = $weblab->get_reservation_status($reservation_status->reservation_id);
		$client_url = $weblab->create_client($reservation_status);
		return $client_url;
		
	}
}

class Experiment
{
	private $gid;
	private $exp_name;
	private $cat_name;
	private $url;

	function __construct($gid, $exp_name, $cat_name, $url) {
		$this->gid = $gid;
		$this->exp_name = $exp_name;
		$this->cat_name = $cat_name;
		$this->url = $url;
	}
	
	function getGid(){
		return $this->gid;
	}

	function getExp_name(){
		return $this->exp_name;
	}

	function getCat_name(){
		return $this->cat_name;
	}

	function getUrl(){
		return $this->url;
	}
}

