<?php
// Check to ensure this file is included in Joomla!
defined('_JEXEC') or die('Restricted access');

jimport('joomla.html.html');
jimport('joomla.form.formfield');
jimport('joomla.form.helper');
require("components/com_weblab/lib/weblabdeusto.class.php");
JFormHelper::loadFieldClass('list');
//include('components/com_linkeddata/configuration.php');

class JFormFieldExperimentSelect extends JFormFieldList {

        protected $type = 'Experimentselect';

	private function getWeblabData(){
		$db = JFactory::getDBO();

                $query = 'SELECT host, user, password FROM #__weblab_config';
                $db->setQuery($query);
                $data = $db->loadRow();
		return $data;
	}

	private function getExperiments() {
		$weblab_data = $this->getWeblabData();
		$weblab = new WebLabDeusto($weblab_data[0]);
		$sess_id = $weblab->login($weblab_data[1],$weblab_data[2]);
		$experiments = $weblab->list_experiments($sess_id);
		return $experiments;
	}


	private function get_joomla_experiments($gid){
		$db = JFactory::getDBO();

                $query = 'SELECT exp_name FROM #__weblab WHERE gid = ' . $gid;
                $db->setQuery($query);
                $experiments = $db->loadResultArray();
		return $experiments;
		
	}

        public function getInput() {
		$gid = -1;
		if (array_key_exists("gid", $_GET)){
                        if ($_GET["gid"] != null) {
				$gid = $_GET["gid"];
			}
		}
			
		$j_experiments = $this->get_joomla_experiments($gid);
		$form = '';
		$form .= '<ul class="checklist usergroups" id="' . $this->id . '" name="' . $this->name . '">';
		$experiments = $this->getExperiments();
		foreach($experiments as $experiment) {
			if (in_array($experiment->name, $j_experiments)) {
				$form .= '<li><input type="checkbox" id="' . $experiment->name  .'" value="' . $experiment->name . ',' . $experiment->category  . '"  name="' . $this->name . '[]" checked /><label for="' . $experiment->name  . '">' . $experiment->name . ' - '  . $experiment->category . '</label></li>' ;
			} else {
				$form .= '<li><input type="checkbox" id="' . $experiment->name  .'" value="' . $experiment->name . ',' . $experiment->category  . '" id="' . $this->id . '" name="' . $this->name . '[]"/><label for="' . $experiment->name  . '">' . $experiment->name . ' - '  . $experiment->category . '</label></li>' ;
			}
		}
		$form .= '</ul>';
	
		return $form;
	}

}
