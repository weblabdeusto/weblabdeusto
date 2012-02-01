<?php
// Check to ensure this file is included in Joomla!
defined('_JEXEC') or die('Restricted access');
 
jimport('joomla.html.html');
jimport('joomla.form.formfield');
jimport('joomla.form.helper');
JFormHelper::loadFieldClass('list');
//include('components/com_linkeddata/configuration.php');
 
class JFormFieldGroupSelect extends JFormFieldList {

	protected $type = 'Groupselect';

	public function getGroups($return_all) {
		$db = JFactory::getDBO();
		
		$query = 'SELECT id, title FROM #__usergroups';
		$db->setQuery($query);
		$groups = $db->loadRowList();
		
		if (!$return_all) {
			$query = 'SELECT gid FROM #__weblab';
                	$db->setQuery($query);
                	$weblab_groups = $db->loadResultArray();

			$return_groups = array();

			foreach($groups as $group) {
				if(!in_array($group[0], $weblab_groups)) {
					array_push($return_groups, $group);
				}
			}

			return $return_groups;
		} else {
			return $groups;
		}
	}

	private function getGroupName($gid) {
		 $db = JFactory::getDBO();

                $query = 'SELECT title FROM #__usergroups WHERE id=' . $gid;
                $db->setQuery($query);
                $group = $db->loadResult();
		return $group;

	}

	public function getInput() {
		if (array_key_exists("gid", $_GET)){
			if ($_GET["gid"] != null) {
				$groups = $this->getGroups(true);
                		$group_id = -1;
				$group_id = $_GET["gid"];
				//$result = '<select id="' . $this->id . '" name="' . $this->name . '">'; // TODO:EL disabled!
				$result = '<label id="' . $this->id  . ' " name="' . $this->name  . '">' . JText::_( 'COM_WEBLAB_WEBLAB_MODIFIYING') . '<b> ' . $this->getGroupName($group_id) .'</b></label>';
				return $result;
			} else {
				$result = '<select id="' . $this->id . '" name="' . $this->name . '">';
				$groups = $this->getGroups(false);
                		$group_id = -1;
			}
		} else {
                	$result = '<select id="' . $this->id . '" name="' . $this->name . '">';
			$groups = $this->getGroups(false);
                	$group_id = -1;
                }

		//$result = '<select id="' . $this->id . '" name="' . $this->name . '">';
		foreach($groups as $group) {
			if ($group[0] == $group_id) {
				$result .= '<option selected="selected" value="' . $group[0]  . '">' . $group[1]  . '</option>';	
			} else {
				$result .= '<option value="' . $group[0]  . '">' . $group[1]  . '</option>';
			}
		}
		$result .= '</select>';
		return $result;
	}
}
