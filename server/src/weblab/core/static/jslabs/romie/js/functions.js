registering = false;

function getAge(milliseconds) {
    var today = new Date();
    var birthDate = new Date(milliseconds);
    var age = today.getFullYear() - birthDate.getFullYear();
    var m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    return age;
}

function start(time, initialConfig) {
	weblab.sendCommand("CHECK_REGISTER")
        .done(function(response) {
            response = JSON.parse(response);
			console.debug("[server check_register response is: ");
			console.debug(response);

			if (response['register']) {
				register(response['psycho']);
			}
            else if (response['psycho']) {
				psycho(response['gender'], response['birthday']*1000, response['grade'], response['user']);
			}
            else {
				init(response['time'], response['points']);
			}

            $(parent.document).find('#exp-frame').show();
            $(parent).scrollTop($(parent.document).find('#exp-frame').position().top, 0);
        });
}

function psycho(gender, birthday, grade, user) {
	$('#labpsico').modal('show');

		weblab.sendCommand("PSYCHO "+points)
            .done(function(response) {
                response = JSON.parse(response);
                init(response['time'], response['points']);
            });
		$('#labpsico').modal('hide');
	}, (gender ? "H" : "M"), getAge(birthday), grade, user);
}

function register(do_psycho) {
	$('#register .modal-footer button').click(function() {
		if ( ! registering) {
			register_ok = true;
			registering = true;

			name = $('#name').val();
			surname = $('#surname').val();
			school = $('#school').val();
			bday = parseInt($('#bday').val());
			bmon = parseInt($('[name=bmon]').val())-1;
			byear = parseInt($('[name=byear]').val());
			email = $('#email').val();
			gender = parseInt($('#gender').val());
			grade = $('#grade').val();

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

			if (byear < 1995 || byear > 2010 || bday < 1 || bmon < 0 || bmon > 11) {
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

				data = {"name":name, "surname":surname, "school":school, "bdate":unix, "email":email, "gender": gender, "grade": grade};

				command = "REGISTER " + JSON.stringify(data);
				weblab.sendCommand(command)
                    .done(function(response) {
                        response = JSON.parse(response);
                        if (response['error'] == "email") {
                            $('#email-group').addClass('has-error');
                            registering = false;
                        } else {
                            $('#register').modal('hide');
                            registering = false;
                            if (do_psycho) {
                                psycho(response['gender'], response['birthday']*1000, response['grade'], response['user']);
                            } else {
                                init(response['time'], response['points']);
                            }
                        }
                    });
			} else {
				registering = false;
			}
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
	setTimeout(function(){if ($('#register').is(':visible')) weblab.cleanExperiment();}, 120000); // 2*60*1000
}

function init(time, points) {
	console.debug("[time is: " + time)
	romie = new Romie();
	game = new Game(time, points);

	$('button.forward').click(function(){if( ! romie.isMoving()) romie.forward(function(question){game.showQuestion(question);})});
	$('button.left').click(function(){if ( ! romie.isMoving()) romie.left();});
	$('button.right').click(function(){if ( ! romie.isMoving()) romie.right();});

	$('#question .modal-footer button').click(function(){game.answerQuestion();});
	$('#response_wrong .modal-footer button').click(function(){$('#response_wrong').modal('hide')});
	$('#response_ok .modal-footer button').click(function(){$('#response_ok').modal('hide')});
	$('#game_end .modal-footer button').click(function(){$('#game_end').modal('hide')});

	$('#game_end').on('hidden.bs.modal', function(){weblab.cleanExperiment()});

	updateCam1 = function() {
		d = new Date();
		$('.camera1 img').attr("src", "https://cams.weblab.deusto.es/webcam/proxied.py/romie_onboard?"+d.getTime());
	};

	$('.camera1 img').on("load", function(){setTimeout(updateCam1, 400)});
	updateCam1();
}

function updateTime(timeLeft) {
	$('.time span').html(Math.floor(timeLeft/60) + ":" + pad(Math.floor(timeLeft%60), 2) + "," + Math.floor((timeLeft%60) * 100-Math.floor(timeLeft%60)*100));
}

function updatePoints(points) {
	$('.points span').html(points);
}
