function pad(n, width, z) {
	z = z || '0';
	n = n + '';
	return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

Game = function(time) {
	this.points = 0;
	this.endTime = new Date(time*1000);
	this.topCamTimmer = null;
	this.timer = null;
	this.topCamTime = 0;

	this.startGame();
}

Game.prototype.startGame = function() {
	this.timer = setInterval(function() {
		time = (this.endTime.getTime()-(new Date()).getTime())/1000;

		$('.time span').html(Math.floor(time/60) + ":" + pad(Math.floor(time%60), 2) + "," + Math.floor((time%60) * 100-Math.floor(time%60)*100));
		if (time <= 0) {
			$('.time span').html("0:00.00");
			this.endGame();
		}
	}.bind(this), 10);
}

Game.prototype.endGame = function() {
	clearInterval(this.timer);

	Weblab.sendCommand("FINISH", function(response) {
		data = JSON.parse(response);
		console.log(data);

		for (i = 0; i < Object.keys(data).length; i++) {
			if (data[i]["current"]) $('#game_end_points').text(data[i]["points"]);
			$('table tbody').append($('<tr>').addClass(data[i]["current"] ? 'success' : '')
				.append($('<td>').text(i+1))
				.append($('<td>').text(data[i]["name"]))
				.append($('<td>').text(data[i]["surname"]))
				.append($('<td>').text(data[i]["school"]))
				.append($('<td>').text(data[i]["points"]))
			);
		}

		$('#game_end').modal('show');
		setTimeout(function(){Weblab.clean();}, 15000); // 15*1000
	});
}

Game.prototype.showQuestion = function(question) {
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

Game.prototype.answerQuestion = function() {
	answer = parseInt($('#question input[name="answer"]:checked').val());

	if ( ! isNaN(answer))
	{
		Weblab.sendCommand("ANSWER " + answer,  function(response) {
			response = JSON.parse(response);

			if (response['correct'])
			{
				this.points = response["points"];
				this.endTime = new Date(response["finish_time"]*1000);

				$('.points span').html(this.points);
				this.topCamTime += 10;
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

		$("#question").modal('hide');
	}
}

// TODO
Game.prototype.getTopCamTime = function()
{
	return this.topCamTime;
}

Game.prototype.isTopCamActive = function()
{
	return this.topCamActive;
}

Game.prototype.deactivateTopCam = function()
{
	this.topCamActive = false;
}

Game.prototype.activateTopCam = function()
{
	this.topCamActive = true;

	this.topCamTimer = setInterval(function()
	{
		if (this.topCamActive)
			this.topCamTime--;
		else
			this.deactivateTopCam();
	}.bind(this), 1000);
}
