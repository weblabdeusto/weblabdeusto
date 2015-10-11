Blockly.Blocks['romie_move_forward'] = {
	init: function() {
		this.setHelpUrl(null);
		this.setColour(65);
		this.appendDummyInput()
			.appendField(getMessage("go_forward"));
		this.setPreviousStatement(true, "null");
		this.setNextStatement(true, "null");
		this.setTooltip('');
	}
};

Blockly.Blocks['romie_turn_left'] = {
	init: function() {
		this.setHelpUrl(null);
		this.setColour(65);
		this.appendDummyInput()
			.appendField(getMessage("turn_left"));
		this.setPreviousStatement(true, "null");
		this.setNextStatement(true, "null");
		this.setTooltip('');
	}
};

Blockly.Blocks['romie_turn_right'] = {
	init: function() {
		this.setHelpUrl(null);
		this.setColour(65);
		this.appendDummyInput()
			.appendField(getMessage("turn_right"));
		this.setPreviousStatement(true, "null");
		this.setNextStatement(true, "null");
	}
};

Blockly.Blocks['romie_wall'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(getMessage("wall_in_front"));
    this.setOutput(true, "Boolean");
    this.setColour(260);
  }
};

Blockly.JavaScript['romie_move_forward'] = function(block) {
	code = 'forward();\n'+
			'while(isMoving());\n';
	return code;
};

Blockly.JavaScript['romie_turn_left'] = function(block) {
	code = 'left();\n'+
			'while(isMoving());\n';
	return code;
};

Blockly.JavaScript['romie_turn_right'] = function(block) {
	code = 'right();\n'+
			'while(isMoving());\n';
	return code;
};

Blockly.JavaScript['romie_wall'] = function(block) {
	var code = '(function() {\n'+
				'    checkWall();\n'+
				'    while(isCheckingWall());\n'+
				'    return lastWallCheck();\n'+
				'})()';
	return [code, Blockly.JavaScript.ORDER_NONE];
};
