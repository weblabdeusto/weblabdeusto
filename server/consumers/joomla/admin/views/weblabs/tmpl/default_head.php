<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted Access');
?>
<tr>	
	<th width="5">
		<input type="checkbox" name="toggle" value="" onclick="checkAll(<?php echo count($this->items); ?>);" />
	</th>
	<th width="0">
		<?php echo JText::_('COM_WEBLAB_WEBLAB_HEADING_GID'); ?>
	</th>			
	<!--<th>
		<?php #echo JText::_('COM_WEBLAB_WEBLAB_HEADING_EXP_NAME'); ?>
	</th>
	<th>
                <?php #echo JText::_('COM_WEBLAB_WEBLAB_HEADING_CAT_NAME'); ?>
        </th>-->

</tr>

