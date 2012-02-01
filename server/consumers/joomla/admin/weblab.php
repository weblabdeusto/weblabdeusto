<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted access');
 
// Set some global property
$document = JFactory::getDocument();
$document->addStyleDeclaration('.icon-48-weblab {background-image: url(../media/com_weblab/images/weblab-48x48.png);}');

// import joomla controller library
jimport('joomla.application.component.controller');
 
// Get an instance of the controller prefixed by HelloWorld
$controller = JController::getInstance('WebLab');
 
// Perform the Request task
$controller->execute(JRequest::getCmd('task'));
 
// Redirect if set by the controller
$controller->redirect();
