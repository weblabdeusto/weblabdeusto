<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted Access');
?>

<?php $item_array = array() ?>
<?php foreach($this->items as $i => $item): ?>
	<tr class="row<?php echo $i % 2; ?>">
		
		<td>
			
			<?php
			if (!in_array($item->gid, $item_array)){
				 echo JHtml::_('grid.id', $i, $item->gid); 
			} ?>
		</td>
		<td>
			<?php
			if (!in_array($item->gid, $item_array)){
				$db = JFactory::getDBO();

                		$query = 'SELECT title FROM #__usergroups WHERE id=' . $item->gid;
                		$db->setQuery($query);
                		$group = $db->loadResult();

				echo $group;
			 	array_push($item_array, $item->gid);
			} ?>
		</td>
		<!--<td>
			<?php #echo $item->exp_name; ?>
		</td>
		 <td>
                        <?php #echo $item->cat_name; ?>
                </td>-->

	</tr>
<?php endforeach; ?>
