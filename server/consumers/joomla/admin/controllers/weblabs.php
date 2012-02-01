<?php
defined('_JEXEC') or die('Restricted access');
 
// import Joomla controlleradmin library
jimport('joomla.application.component.controlleradmin');
 
/**
 * HelloWorlds Controller
 */
class WebLabControllerWebLabs extends JControllerAdmin
{
        /**
         * Proxy for getModel.
         * @since       1.7
         */
        public function getModel($name = 'WebLab', $prefix = 'WebLabModel')         
        {
                $model = parent::getModel($name, $prefix, array('ignore_request' => true));
                return $model;
        }
}

