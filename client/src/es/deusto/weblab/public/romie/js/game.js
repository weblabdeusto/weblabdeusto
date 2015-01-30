Game = function(romie, updater)
{
	this.romie = romie;
}

Game.prototype.updateNumbers = function(show_question)
{
	show_question = typeof show_question === 'boolean' ? show_question : true;
	movements = romie.getMovements();
	points = romie.getPoints();

	// TODO format

	$('.movements span').html(movements);
	$('.points span').html(points);

	if (movements == 0)
	{
		$('#game_end_points').text(romie.getPoints());
		$('#game_end').modal('show');
	}
	else if (show_question && romie.hasTag())
	{
		game.showQuestion(game.getQuestion(romie.getTag()));
	}
}

Game.prototype.showQuestion = function(question)
{
	console.log(question);
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
					if (this.question["type"] == 0)
					{
						this.romie.addPoints(this.question["points"]);
						this.romie.addMovements(this.question["movements"]);
					}
					else
					{
						this.romie.setPoints(this.question["points"]*this.romie.getPoints());
						this.romie.setMovements(this.question["movements"]*this.romie.getMovements());
					}
					this.updateNumbers(false);
					this.romie.setTopCamTime(10);
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