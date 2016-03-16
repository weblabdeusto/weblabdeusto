function pad(n, width, z) {
	z = z || '0';
	n = n + '';
	return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

Game = function(time, points) {
	this.points = points;
	this.endTime = new Date(time*1000);
    console.debug("[ time * 1000 is: " + time * 1000);
	this.topCamTimmer = null;
	this.timer = null;
	this.cameraStartTime = null;

	this.startGame();
};

Game.prototype.startGame = function() {
	this.timer = setInterval(function() {
		time = (this.endTime.getTime()-(new Date()).getTime())/1000;
        // console.debug("[ time in startGame: " + time);
		updateTime(time);
		if (time <= 0) {
			updateTime(0);
			this.endGame();
		}
	}.bind(this), 10);
	updatePoints(this.points);
};

Game.prototype.endGame = function() {
	clearInterval(this.timer);

	weblab.sendCommand("FINISH")
        .done(function(response) {
            data = JSON.parse(response);

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
            setTimeout(function(){weblab.cleanExperiment();}, 20000);
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

	$('#question').on('hidden.bs.modal', function() {
		this.question = {};
		$('#questionLabel').html("");
		$('#question .modal-body form').html("");
	}.bind(this));
}

Game.prototype.answerQuestion = function() {
	answer = parseInt($('#question input[name="answer"]:checked').val());

	if ( ! isNaN(answer)) {
		weblab.sendCommand("ANSWER " + answer)
            .done(function(response) {
                response = JSON.parse(response);

                if (response['correct']) {
                    this.points = response["points"];

                    // BUG: THE FINISH TIME IS BEING TAKEN FROM THE SERVER, AND LATER COMPARED
                    // TO CLIENT-SIDE TIME. THIS CAN LEAD TO MANY PROBLEMS.
                    this.endTime = new Date(response["finish_time"]*1000);

                    updatePoints(this.points);
                    $('#response_ok').modal('show');
                    $('#response_ok').on('hidden.bs.modal', function() {
                        if ($('.camera2').hasClass('inactive')) {
                            $('.camera2').removeClass('inactive');
                            $('.camera2').addClass('active');
                            $('.camera2').click(function() {
                                $('.camera2 p').hide();
                                $('.camera2').unbind('click');
                                cameraStartDate = new Date();

                                var onCameraLoad = function(event) {
                                    setTimeout(function(startDate) {
                                        d = new Date();
                                        if (startDate > (d.getTime()-15000)) {
                                            $('.camera2 img').attr("src", "https://cams.weblab.deusto.es/webcam/proxied.py/romie_top?"+d.getTime());
                                        } else {
                                            $('.camera2').removeClass('active');
                                            $('.camera2').addClass('inactive');
                                            $('.camera2 img').attr('src', 'img/black.png');
                                            $('.camera2 p').removeAttr('style');
                                            $('.camera2 img').off('load');
                                        }
                                    }, 400, event.data.startDate);
                                };

                                $('.camera2 img').on("load", {startDate: cameraStartDate.getTime()}, onCameraLoad);
                                $('.camera2 img').on("error", onCameraLoad);

                                $('.camera2 img').attr("src", "https://cams.weblab.deusto.es/webcam/proxied.py/romie_top?"+cameraStartDate.getTime());
                            });
                        }
                    });
                } else {
                    $('#response_wrong').modal('show');
                }
            }.bind(this));

		$("#question").modal('hide');
	}
}
