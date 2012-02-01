<?php
  #@TODO: uncomment
  #defined('JEXEC') or die('Restricted access');

  jimport('joomla.application.component.controller');

  $controller = JController::getInstance('WebLab');

  $controller->execute(JRequest::getCmd('task'));

  $controller->redirect();
?>
