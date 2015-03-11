angular
    .module("lab")
    .controller("LabController", LabController);


function LabController($scope, $injector) {

    // -------------------------
    // Save self-reference and do some initialization.
    // -------------------------

    var controller = this;

    // Initialize the Weblab API.
    var json_url = "{{ json_url }}";
    WeblabWeb.setTargetURLs(json_url, json_url);


    // -------------------------
    // Requirements
    // -------------------------

    var $log = $injector.get('$log');


    // -------------------------
    // Scope data
    // -------------------------

    $scope.experiment = {};
    $scope.experiment.active = false;

    $scope.reserveMessage = {
        message: '',
        type: 'info'
    };


    // -------------------------
    // Scope methods
    // -------------------------

    $scope.reserveInFrame = reserveInFrame;
    $scope.reserveInWindow = reserveInWindow;
    $scope.isExperimentActive = isExperimentActive;


    // -------------------------
    // Implementations
    // -------------------------

    /**
     * Checks whether the experiment is active.
     *
     * @return {bool}: True if the reserve has been done and the experiment has not finished yet. False otherwise.
     */
    function isExperimentActive() {
        return $scope.experiment.active;
    }

    /**
     * Called to reserve the experiment in the frame.
     */
    function reserveInFrame() {
        var sessionid = "{{ request.cookies.get('weblabsessionid') }}";
        sessionid = sessionid.split(".", 1)[0];

        var name = "{{ experiment['name'] }}";
        var category = "{{ experiment['category'] }}";

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

                    $scope.$apply();
                }
            })
            .fail(function (error) {
                onReserveFail(error);
            })
            .done(function (uid, time, initial_config, result) {

                console.log("Experiment now active");
                $scope.experiment.active = true;
                console.log("SETTING EXPERIMENT TO ACTIVE. SCOPE: ");
                console.log($scope.$id);

                $scope.reserveMessage.message = "{{ gettext('Reservation done') }}";
                $scope.reserveMessage.type = 'info';

                var frame = $("#exp-frame")[0];
                var wexp = frame.contentWindow.weblabExp; // This value is hard-coded in the experiment's HTML. // TODO: Make it prettier.
                currentExperiment = wexp; // Save it in a GLOBAL. // TODO: Consider tiding it up.
                var url = result["url"];
                var json_url = "{{ json_url }}";
                wexp.setTargetURL(json_url);
                wexp._reservationReady(result["reservation_id"]["id"], result["time"], result["starting_config"]);

                // Listen also for a dispose, for other ui changes.
                wexp.onFinish().done(function (f) {
                    $scope.experiment.active = false;

                    onExperimentFinished();

                    $scope.$apply();
                });

                $scope.$apply();
            });
    }

    function reserveInWindow() {
        var sessionid = "{{ request.cookies.get('weblabsessionid') }}";
        sessionid = sessionid.split('.')[0];

        var name = "{{ experiment['name'] }}";
        var category = "{{ experiment['category'] }}";

        $(".reserve-free-btn").attr("disabled", "");
        $scope.reserveMessage.message = "{{ gettext('Reserving experiment...') }}";
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
                // We logged out.
                if (error.code == "JSON:Client.SessionNotFound") {
                    errorStatus("{{ gettext("You are not logged in") }}");
                    setTimeout(function () {
                        window.location = "{{ url_for(".index") }}";
                    }, 1500);
                }
                else {
                    errorStatus("{{ gettext("Failed to reserve: ") }}" + error.message)
                }
            })
            .done(function (id, time, initConfig, result) {
                console.log("RESERVATION DONE");
                console.log(result);

                $scope.reserveMessage.message = "{{ gettext('Reservation done') }}";
                $scope.reserveMessage.type = 'info';


                {# TODO: Tidy this up. #}
                {% if experiment["type"] == "js" %}

                    var params = {
                        "r": id,
                        "c": initConfig,
                        "t": time,
                        "u": "{{ json_url }}",
                        "free": "true"
                    };
                    {# //var redir = "{{ '//rawgit.com/weblabdeusto/weblabdeusto/new_client/client/src/es/deusto/weblab/public/' + experiment["html.file"] }}"; #}
                    var redir = "{{ lab_url + experiment['config']['html.file'] }}";
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
    } //! reserveInWindow()

} //! LabController
