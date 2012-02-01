<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted access');
 
// import Joomla view library
jimport('joomla.application.component.view');
 
/**
 * HelloWorld View
 */
class WebLabViewWebLab extends JView
{

	protected $form = null;

	/**
	 * display method of Hello view
	 * @return void
	 */
	public function display($tpl = null) 
	{
		// get the Data
		$form = $this->get('Form');
		$item = $this->get('Item');
 
		// Check for errors.
		if (count($errors = $this->get('Errors'))) 
		{
			JError::raiseError(500, implode('<br />', $errors));
			return false;
		}
		// Assign the Data
		$this->form = $form;
		$this->item = $item;
 
		// Set the toolbar
		$this->addToolBar();
 
		// Display the template
		parent::display($tpl);

		// Set the document
		$this->setDocument();
	}
 
	/**
	 * Setting the toolbar
	 */
	protected function addToolBar() 
	{
		JRequest::setVar('hidemainmenu', true);
		$isNew = ($this->item->gid == 0);
		JToolBarHelper::title($isNew ? JText::_('COM_WEBLAB_MANAGER_WEBLAB_NEW')
		                             : JText::_('COM_WEBLAB_MANAGER_WEBLAB_EDIT'));
		JToolBarHelper::save('weblab.save');
		JToolBarHelper::cancel('weblab.cancel', $isNew ? 'JTOOLBAR_CANCEL'
		                                                   : 'JTOOLBAR_CLOSE');
	}

	protected function setDocument() 
	{
		$isNew = ($this->item->gid < 1);
		$document = JFactory::getDocument();
		$document->setTitle($isNew ? JText::_('COM_WEBLAB_WEBLAB_CREATING')
		                           : JText::_('COM_WEBLAB_WEBLAB_EDITING'));
	}
}
