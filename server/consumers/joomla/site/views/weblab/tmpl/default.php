<?php
// No direct access to this file
defined('_JEXEC') or die('Restricted access');
?>
<?php

echo "<table border=\"1\"><tr>
<th>" . JText::_('COM_WEBLAB_WEBLAB_HEADING_GID')  . "</th>
<th>" . JText::_('COM_WEBLAB_WEBLAB_HEADING_EXP_NAME')  . "</th>
<th>" . JText::_('COM_WEBLAB_WEBLAB_HEADING_CAT_NAME')  . "</th>
<th>" . JText::_('COM_WEBLAB_WEBLAB_HEADING_URL')  . "</th>
</tr>";
 
foreach($this->experiments as $gid => $experiment) {
	echo "<tr><td>" . $experiment->getGid() ."</td><td>" . $experiment->getExp_name() . "</td><td>" . $experiment->getCat_name()  ."</td><td><form method=\"POST\" action=\"" . $experiment->getUrl()  . "\"><input type=\"submit\" value=\"Run\"></form></td></tr>";
}

echo "</table>"


?>
