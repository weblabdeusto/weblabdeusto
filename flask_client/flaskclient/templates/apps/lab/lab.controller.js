angular
    .module("lab")
    .controller("LabController", LabController);


function LabController($scope) {
    $scope.experiment = {};
    $scope.experiment.active = false;

    $scope.reserveInFrame = reserveInFrame;
    $scope.reserveInWindow = reserveInWindow;

    // To check whether the experiment is active (reserve done and has not ended).
    $scope.isExperimentActive = isExperimentActive;

    $scope.reserveMessage = {
        message: '',
        type: 'info'
    };


    /**
     * Checks whether the experiment is active.
     *
     * @return {bool}: True if the reserve has been done and the experiment has not finished yet. False otherwise.
     */
    function isExperimentActive() {
        return $scope.experiment.active;
    }

    function reserveInFrame() {
        var sessionid = "{{ request.cookies.get('sessionid') }}";
        var name = "{{ experiment['experiment.name'] }}";
        var category = "{{ experiment['experiment.category'] }}";

        $(".reserve-btn").attr("disabled", "");

        $scope.reserveMessage.message = "{{ gettext('Reserving...') }}";
        $scope.reserveMessage.type = 'info';

        WeblabWeb.reserve_experiment(sessionid, name, category)
            .progress(function (status, position, result) {
                if (position != undefined) {
                    if (position == 0) {
                        $scope.reserveMessage.message = "{{ gettext('Waiting in the queue. You are next.') }}";
                        $scope.reserveMessage.type = 'info';
                    }
                    else {
                        $scope.reserveMessage.message = "{{ gettext('Waiting in the queue. Your position is: ') }}" + position + ".";
                        $scope.reserveMessage.type = 'info';
                    }
                }
            })
            .fail(function (error) {
                onReserveFail(error);
            })
            .done(function (uid, time, initial_config, result) {

                $scope.experiment.active = true;

                $scope.reserveMessage.message = "{{ gettext('Reservation done') }}";
                $scope.reserveMessage.type = 'info';

                var frame = $("#exp-frame")[0];
                var wexp = frame.contentWindow.Weblab.getWeblabExp();
                currentExperiment = wexp; // Save it in a GLOBAL. // TODO: Consider tiding it up.
                var url = result["url"];
                wexp.setTargetURL("{{ url_for('redir_json', _external=True) }}");
                wexp._reservationReady(result["reservation_id"]["id"], result["time"], result["starting_config"]);

                // Listen also for a dispose, for other ui changes.
                wexp.onFinish().done(function (f) {
                    $scope.experiment.active = false;

                    onExperimentFinished();
                });

                // For some ui changes.
                onReserveDone();
            });
    }

    function reserveInWindow() {
        console.log("FREE RESERVE PROC STARTED");
        var sessionid = "{{ request.cookies.get('sessionid') }}";
        var name = "{{ experiment['experiment.name'] }}";
        var category = "{{ experiment['experiment.category'] }}";

        $(".reserve-free-btn").attr("disabled", "");
        infoStatus("{{ gettext('Reserving experiment...') }}");

        WeblabWeb.reserve_experiment(sessionid, name, category)
            .fail(function (error) {
                onReserveFail(error);
            })
            .done(function (id, time, initConfig, result) {
                console.log("RESERVATION DONE");
                console.log(result);

                infoStatus("{{ gettext('Reservation done') }}");


                {# TODO: Tidy this up. #}
                {% if experiment_type == "js" %}

                    var params = {
                        "r": id,
                        "c": initConfig,
                        "t": time,
                        "u": "{{ url_for("redir_json", _external=True) }}",
                        "free": "true"
                    };
                    {# //var redir = "{{ '//rawgit.com/weblabdeusto/weblabdeusto/new_client/client/src/es/deusto/weblab/public/' + experiment["html.file"] }}"; #}
                    var redir = "{{ config['LAB_URL'] + experiment['html.file'] }}";
                    redir += "?" + $.param(params);
                    console.log(redir);

                    window.location = redir;

                {# We assume it is a REDIRECT (HTTP) experiment #}
                {% else %}

                    // If it is indeed a REDIRECT (HTTP) experiment, then initConfig of the reservation will
                    // contain an "url" attribute, which is the URL to which to redirect.
                    console.log("ON REDIR");

                    var parsedConfig = JSON.parse(initConfig);
                    var url = parsedConfig["url"];


                    // Replace TIME_REMAINING if present. Seems to be somewhat standard.
                    url = url.replace("TIME_REMAINING", Math.floor(time));

                    if(url == undefined) {
                        console.error("EXPERIMENT DOES NOT SEEM TO BE OF REDIRECT TYPE: NO URL PROVIDED.");
                        WeblabWeb.finishExperiment(); // Abort the experiment.
                        return;
                    }

                    // Redirect to the provided address.
                    console.log("Redirecting to: " + url);
                    window.location = url;

                {% endif %}


            });
    }

} //! LabController
