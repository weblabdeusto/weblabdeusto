Game = function(romie)
{
	this.romie = romie;
}

Game.prototype.showQuestion = function(question)
{
	question = JSON.parse(question);

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

	$("#question").modal('hide');

	Weblab.sendCommand("ANSWER "+answer+" "+this.question["difficulty"]+" "+
		this.question["index"]+" "+this.question["category"], function(response)
		{
			if (response == 'true')
			{
				$('#response_ok').modal('show');
				// TODO show dialog + add points & movements
			}
			else
			{
				// TODO show dialog
			}
			// TODO clear question
		});
}

Game.prototype.getQuestion = function(tag)
{
	//TODO
	difficulty = Math.floor(this.romie.getPoints()/500);
	category = "general";

	Weblab.sendCommand("QUESTION "+difficulty+" "+category, function(response){this.showQuestion(response);}.bind(this));
}