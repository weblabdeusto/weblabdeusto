<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted access');
 
// import Joomla modelitem library
jimport('joomla.application.component.modelitem');
 
/**
 * HelloWorld Model
 */
class WebLabModelWebLab extends JModelItem
{
	/**
	 * @var string msg
	 */
	protected $exp_array;
	protected $username;

	/**
	 * Returns a reference to the a Table object, always creating it.
	 *
	 * @param	type	The table type to instantiate
	 * @param	string	A prefix for the table class name. Optional.
	 * @param	array	Configuration array for model. Optional.
	 * @return	JTable	A database object
	 * @since	1.7
	 */
	public function getTable($type = 'WebLab', $prefix = 'WebLabTable', $config = array()) 
	{
		return JTable::getInstance($type, $prefix, $config);
	}
 
	/**
	 * Get the message
	 * @return string The message to be displayed to the user
	 */
	public function getExperiments() 
	{
		if (!isset($this->exp_array)) 
		{
			$this->exp_array = $this->loadExperiments();
		}
		return $this->exp_array;
	}
	
	public function getUserName() {
		if(!isset($this->username)) {
			$user = JFactory::getUser();
			$this->username = $user->name;
		}
		return $this->username;
	}

        private function loadExperiments() {
		$user = JFactory::getUser();
		$gids = $user->groups;
		$db = JFactory::getDBO();
		$exp_array = array();
		$exp_names = array();
		foreach ($gids as $gid) {
			$query = "SELECT gid, exp_name, cat_name FROM #__weblab WHERE gid = " . $gid;
			$db->setQuery($query);
			$rows = $db->loadRowList();
		 	//$exp_array = $exp_array + $rows;
			//array_push($exp_array, $rows);
			foreach($rows as $row){
				if(!in_array($row[1], $exp_names)) {			
					array_push($exp_array, $row);
					array_push($exp_names, $row[1]);
				}
			}
		}
		return $exp_array;
	}
}
