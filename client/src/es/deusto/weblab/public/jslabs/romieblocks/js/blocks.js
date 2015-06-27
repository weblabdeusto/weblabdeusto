Blockly.Blocks['romie_move_forward'] = {
	init: function() {
		this.setHelpUrl(null);
		this.setColour(65);
		this.appendDummyInput()
			.appendField("Ir recto");
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
			.appendField("Girar a la izquierda");
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
			.appendField("Girar a la derecha");
		this.setPreviousStatement(true, "null");
		this.setNextStatement(true, "null");
	}
};

Blockly.Blocks['romie_wall'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("hay una pared");
    this.setOutput(true, "Boolean");
    this.setColour(260);
  }
};

// Blockly.Blocks['romie_no_wall'] = {
//   init: function() {
//     this.appendDummyInput()
//         .appendField("no hay una pared");
//     this.setOutput(true, "Boolean");
//     this.setColour(260);
//   }
// };

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
	// TODO: Assemble JavaScript into code variable.
	var code = '(function() {\n'+
				'    checkWall();\n'+
				'    while(isCheckingWall());\n'+
				'    return lastWallCheck();\n'+
				'})()';
	// TODO: Change ORDER_NONE to the correct strength.
	return [code, Blockly.JavaScript.ORDER_NONE];
};

// Blockly.JavaScript['romie_no_wall'] = function(block) {
// 	// TODO: Assemble JavaScript into code variable.
// 	var code = 'checkWall();'+
// 				'while(isRomieChecking());'+
// 				'lastWallCheck();';
// 	// TODO: Change ORDER_NONE to the correct strength.
// 	return [code, Blockly.JavaScript.ORDER_NONE];
// };
