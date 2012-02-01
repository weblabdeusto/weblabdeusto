<?php
defined('_JEXEC') or die('Restricted access');
JHtml::_('behavior.tooltip');
?>
<form action="<?php echo JRoute::_('index.php?option=com_weblab&layout=edit&id='.(int) $this->item->gid); ?>"
      method="post" name="adminForm" id="weblab-form">
        <fieldset class="adminform">
                <legend><?php echo JText::_( 'COM_WEBLAB_WEBLAB_DETAILS' ); ?></legend>
		<div class="width-60 fltlft">	
                <!--<ul class="adminformlist">-->
<?php foreach($this->form->getFieldset() as $field): ?>
			
                        <!--<li>--><fieldset class="adminform"><legend><?php echo $field->label;?></legend><?php echo $field->input;?></fieldset><!--</li> -->
			
<?php endforeach; ?>
                <!--</ul>-->
		<div/>
        </fieldset>

        <div>
                <input type="hidden" name="task" value="weblab.edit" />
                <?php echo JHtml::_('form.token'); ?>
        </div>
</form>

