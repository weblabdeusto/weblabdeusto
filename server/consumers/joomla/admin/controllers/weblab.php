<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted access');
 
// import Joomla controllerform library
jimport('joomla.application.component.controllerform');
 
/**
 * HelloWorld Controller
 */
class WebLabControllerWebLab extends JControllerForm
{

        public function save($key=null, $urlVar=null){
                
                
		$db =& JFactory::getDBO();

		$exp_array = array();

		$data = JRequest::getVar('jform', array(), 'post', 'array');

		$usergroup = 0;
	
		if($_GET["id"] == 0) {
			$usergroup = $data['usergroup'];
		} else {
			$usergroup = $_GET['id'];
		}
		
		foreach($data['experimentselect'] as $experiment) {
			$experiment_array = explode(',', $experiment);
			array_push($exp_array, $experiment_array[0]);
			$query = "SELECT gid FROM #__weblab WHERE gid = " . $usergroup  . " AND exp_name='" . $experiment_array[0]  . "' AND cat_name='" . $experiment_array[1]  . "'";
               	 	$db->setQuery($query);
                	$column = $db->loadResultArray();
		 	if (empty($column)) {
				$query = "INSERT INTO #__weblab (gid, exp_name, cat_name) VALUES (" . $usergroup . ", '" . $experiment_array[0] . "','" . $experiment_array[1] . "')";
                		$db->setQuery($query);
                		$db->query();
			}	
		}

		$query = "SELECT exp_name FROM #__weblab WHERE gid = " . $usergroup;
		$db->setQuery($query);
                $column = $db->loadResultArray();
	
		foreach($column as $exp_name) {
			if(!in_array($exp_name, $exp_array)) {
				$query = "DELETE FROM #__weblab WHERE exp_name='" . $exp_name .  "' AND gid=" . $usergroup;
				$db->setQuery($query);
                                $db->query();		
			}
		}	
		//print_r(parent::save($key, $urlVar));		               
		parent::cancel();	
        }

}



