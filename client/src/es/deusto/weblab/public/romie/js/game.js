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

	if ( ! isNaN(answer))
	{
		$("#question").modal('hide');

		Weblab.sendCommand("ANSWER "+answer+" "+this.question["difficulty"]+" "+
			this.question["index"]+" "+this.question["category"], function(response)
			{
				if (response == 'True')
				{
					// TODO show dialog + add points & movements
					console.log(this.question['points']);
					if (this.question["type"] == 0)
					{
						this.romie.addPoints(this.question["points"]);
					}
					else
					{
						this.romie.setPoints(this.question["points"]*this.romie.getPoints())
					}
					$('#response_ok').modal('show');
				}
				else
				{
					$('#response_wrong').modal('show');
				}

				this.question = {};
				$('#questionLabel').html("");
				$('#question .modal-body form').html("");
			}.bind(this));
	}
}

Game.prototype.getQuestion = function(tag)
{
	//TODO
	difficulty = Math.floor(this.romie.getPoints()/500);
	category = "general";

	Weblab.sendCommand("QUESTION "+difficulty+" "+category, function(response){this.showQuestion(response);}.bind(this));
}