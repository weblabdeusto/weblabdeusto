Game = function(romie)
{
	this.romie = romie;
}

Game.prototype.showQuestion = function(question)
{
	$('#questionLabel').html(question["question"]);

	i = 0;
	question["answers"].forEach(function(answer)
	{
		$('#question .modal-body form')
			.append('<input type="radio" name="answer" id="ans_'+i+'" value="'+i+'">'+
				'<label for="ans_'+i+'">'+answer+'</label><br>');
		i++;
	}.bind(i));
	$("#question").modal({keyboard:false});

	this.question = question;
}

Game.prototype.answerQuestion = function()
{
	answer = parseInt($('#question input[name="answer"]:checked').val());
	console.log(answer);
	// Get answer
	// Send command
	//    if correct -> show dialog + add points & movements
	//    if incorrect -> show dialog
	// Hide question
	// clear question
}