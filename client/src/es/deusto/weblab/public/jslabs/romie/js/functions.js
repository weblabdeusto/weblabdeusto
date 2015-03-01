function start() {
	Weblab.sendCommand("CHECK_REGISTER", function(response) {
		if (response == "REGISTER") register();
		else init(response);

		$(parent.document).find('iframe[name=wlframe]').show();
		$(parent).scrollTop($(parent.document).find('iframe[name=wlframe]').position().top, 0);
	});
}

function register() {

	$('#register .modal-footer button').click(function() {

		register_ok = true;

		name = $('#name').val();
		surname = $('#surname').val();
		school = $('#school').val();
		bday = parseInt($('#bday').val());
		bmon = parseInt($('[name=bmon]').val())-1;
		byear = parseInt($('[name=byear]').val());
		email = $('#email').val();

		if (name.length < 3 || surname.length < 3) {
			register_ok = false;
			$('#name-group').addClass('has-error');
		}

		if (school.length < 3) {
			register_ok = false;
			$('#school-group').addClass('has-error');
		}

		email_regex = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

		if ( ! email_regex.test(email)) {
			register_ok = false;
			$('#email-group').addClass('has-error');
		}

		if (byear < 1950 || byear > 2010 || bday < 1 || bmon < 0 || bmon > 11) {
			register_ok = false;
			$('#bday-group').addClass('has-error');
		} else {
			daysInMonth = [31,28,31,30,31,30,31,31,30,31,30,31];
			if (( ! (byear % 4) && byear % 100) || ! (byear % 400))
				daysInMonth[1] = 29;

			if (bday > daysInMonth[bmon]) {
				register_ok = false;
				$('#bday-group').addClass('has-error');
			}
		}

		if (register_ok) {
			bdate = new Date(byear, bmon, bday, 12, 0, 0, 0);
			unix = Math.floor(bdate.getTime()/1000);

			data = {"name":name, "surname":surname, "school":school, "bdate":unix, "email":email};

			command = "REGISTER " + JSON.stringify(data);
			Weblab.sendCommand(command, function(response) {
				time = parseFloat(response);
				$('#register').modal('hide');
				init(time);
			});
		}
	});

	$('#name').focusin(function(){$('#name-group').removeClass('has-error');});
	$('#surname').focusin(function(){$('#name-group').removeClass('has-error');});
	$('#school').focusin(function(){$('#school-group').removeClass('has-error');});
	$('#bday').focusin(function(){$('#bday-group').removeClass('has-error');});
	$('[name=bmon]').focusin(function(){$('#bday-group').removeClass('has-error');});
	$('[name=byear]').focusin(function(){$('#bday-group').removeClass('has-error');});
	$('#email').focusin(function(){$('#email-group').removeClass('has-error');});

	$('#register').modal('show');
	setTimeout(function(){if ($('#register').is(':visible')) Weblab.clean();}, 120000); // 2*60*1000
}

function init(time) {

	romie = new Romie();
	game = new Game(time);
	onboard = 'https://www.weblab.deusto.es/webcam/proxied.py/romie_onboard';
	topCam = 'https://www.weblab.deusto.es/webcam/proxied.py/romie_top';
	big = onboard;

	$('button.forward').click(function(){if( ! romie.isMoving()) romie.forward(function(question){game.showQuestion(question);})});
	$('button.left').click(function(){if ( ! romie.isMoving()) romie.left();});
	$('button.right').click(function(){if ( ! romie.isMoving()) romie.right();});

	$('#question .modal-footer button').click(function(){game.answerQuestion();}.bind(game));
	$('#response_wrong .modal-footer button').click(function(){$('#response_wrong').modal('hide')});
	$('#response_ok .modal-footer button').click(function(){$('#response_ok').modal('hide')});
	$('#game_end .modal-footer button').click(function(){$('#game_end').modal('hide')});

	$('#game_end').on('hidden.bs.modal',function(){Weblab.clean()});

	updateCam1 = function() {
		d = new Date();
		$('.camera1 img').attr("src", big+"?"+d.getTime());
	}

	$('.camera1 img').bind("load",function(){setTimeout(updateCam1, 400)});
	updateCam1();

	updateCam2 = function() {
		if (game.isTopCamActive() && game.topCamTime() > 0)
		{
			d = new Date();
			$('.camera2 img').attr('src', onboard+'?'+d.getTime());
		}
		else if (game.isTopCamActive())
		{
			game.deactivateTopCam();
			big = onboard;
			$('.camera2 img').attr('src', 'img/black.png');
		}
	}

	$('.camera2 img').bind('load',function(){setTimeout(updateCam2, 400)});
	updateCam2();

	$('.camera2 img').click(function() //TODO Seems that it does not work properly
	{
		if (game.topCamTime() > 0 && ! game.isTopCamActive())
		{
			big = topCam;
			game.activateTopCam();
		}
		else if (game.topCamTime() > 0)
		{
			game.deactivateTopCam();
			big = onboard;
			clearInterval(camera2);
			$('.camera2 img').attr('src', 'img/black.png');
		}
	});
}