angular
    .module("lab", ['pascalprecht.translate'])
    .config(['$translateProvider', translateConfig])
    .controller("LabController", LabController);

function translateConfig($translateProvider) {
    $translateProvider.useUrlLoader(LOCALES_URL);
    $translateProvider.preferredLanguage(PREFERRED_LANGUAGE);
}

function LabController($scope, $injector) {

    // -------------------------
    // Save self-reference
    // -------------------------

    var controller = this;


    // -------------------------
    // Requirements
    // -------------------------

    var $log = $injector.get('$log');
    var $rootScope = $injector.get('$rootScope');


    // -------------------------
    // Scope data
    // -------------------------

    $scope.experiment = {};
    $scope.experiment.data = {{ experiment|tojson }};
    $scope.experiment.reserving = false;
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
    $scope.isExperimentReserving = isExperimentReserving;
    $scope.finishExperiment = finishExperiment;


    // ------------------------
    // Controller methods
    // ------------------------
    controller.handleReserveProgress = handleReserveProgress;
    controller.handleReserveFail = handleReserveFail;


    // ------------------------
    // Initialization
    // ------------------------

    // Initialize the Weblab API.
    WeblabWeb.setTargetURLs(WL_JSON_URL, WL_JSON_URL);




    // -------------------------
    // Implementations
    // -------------------------

    /**
     * Called when an attempt is made to finish the current experiment.
     */
    function finishExperiment() {
        window.currentExperiment.finishExperiment();
    } // !finishExperiment

    /**
     * Checks whether the experiment is being reserved.
     */
    function isExperimentReserving() {
        return $scope.experiment.reserving;
    }


    /**
     * Checks whether the experiment is active.
     *
     * @return {bool}: True if the reserve has been done and the experiment has not finished yet. False otherwise.
     */
    function isExperimentActive() {
        return $scope.experiment.active;
    }

    /**
     * Handles a reserve progress update, received periodically while a reserve attempt is in progress.
     */
    function handleReserveProgress(status, position, result, broken) {

        if (!broken) {
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
        } else if(broken) {
            if (position != undefined) {
                if (position == 0) {
                    $scope.reserveMessage.message = "{{ gettext('The experiment seems to be broken and no instances are available. Even though, you are first the queue.') }}";
                    $scope.reserveMessage.type = 'danger';
                }
                else {
                    $scope.reserveMessage.message = "{{ gettext('The experiment seems to be broken and no instances are available. Even though, you are waiting in the queue. Your position is: ') }}" + position + ".";
                    $scope.reserveMessage.type = 'danger';
                }

                $scope.$apply();
            } else {
                $scope.reserveMessage.message = "{{ gettext('The experiment seems to be broken. We will keep trying, but for now, reserve will probably fail.') }}";
                $scope.reserveMessage.type = 'danger';
            }
        }
    } // !handleReserveProgress

    /**
     * Handles a reserve failure.
     * @param error
     */
    function handleReserveFail(error) {
        // We logged out.
        if (error.code == "JSON:Client.SessionNotFound") {
            $scope.reserveMessage.message = '{{ gettext("You are not logged in") }}';
            $scope.reserveMessage.type = 'danger';
            setTimeout(function () {
                window.location = '{{ url_for(".login") }}';
            }, 1500);
        }
        else {
            $scope.reserveMessage.message = '{{ gettext("Failed to reserve: ") }}' + error.message;
            $scope.reserveMessage.type = 'danger';
        }

        $scope.$apply();
    } // !handleReserveFail

    /**
     * Called to reserve the experiment in the frame.
     */
    function reserveInFrame() {
        var sessionid = "{{ request.cookies.get('weblabsessionid') }}";
        sessionid = sessionid.split(".", 1)[0];

        var name = "{{ experiment['name'] }}";
        var category = "{{ experiment['category'] }}";

        $scope.experiment.reserving = true;
        $scope.reserveMessage.message = "{{ gettext('Reserving...') }}";
        $scope.reserveMessage.type = 'info';

        WeblabWeb.reserve_experiment(sessionid, name, category)
            .progress(handleReserveProgress)
            .fail(handleReserveFail)
            .done(function (uid, time, initial_config, result) {

                console.log("Experiment now active");
                $scope.experiment.active = true;
                $scope.experiment.reserving = false;
                console.log("SETTING EXPERIMENT TO ACTIVE. SCOPE: ");
                console.log($scope.$id);

                $scope.reserveMessage.message = "{{ gettext('Reservation done') }}";
                $scope.reserveMessage.type = 'info';

                var frame = $("#exp-frame")[0];
                var Wexp = frame.contentWindow.WeblabExp;

                // If wexp is undefined, then it is likely that the experiment loaded in the iframe does not actually
                // support being embedded in the weblab client. In this case, we will report a custom error.
                if(Wexp == undefined || Wexp.lastInstance == undefined) {
                    var error = {
                        message: "{{ gettext('The experiment does not seem to support iframe mode') }}",
                        code: "JSON:ClientSideError:IframeModeNotSupported"
                    };
                    $scope.experiment.active = false;
                    $scope.experiment.reserving = false;
                    handleReserveFail(error);
                    return;
                    // TODO: For now, we return. The experiment is actually reserved successfully, but we cannot
                    // go on because the library does not work as expected.
                }

                // TODO: Consider checking whether WeblabExp version is the expected one.

                var wexp = Wexp.lastInstance;

                window.currentExperiment = wexp; // Save it in a GLOBAL.
                var url = result["url"];
                wexp.setTargetURL(WL_JSON_URL);
                wexp._reservationReady(result["reservation_id"]["id"], result["time"], result["starting_config"]);

                // Listen also for a dispose, for other ui changes.
                wexp.onFinish().done(function (f) {
                    $scope.experiment.active = false;

                    $scope.reserveMessage.message = "";

                    // Broadcast an event, in case some component needs to know.
                    // The iframe, for example, needs to be auto-restarted when this happens.
                    $rootScope.$broadcast("experimentFinished");

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


        $scope.experiment.reserving = true;
        $scope.reserveMessage.message = "{{ gettext('Reserving experiment...') }}";
        $scope.reserveMessage.type = 'info';

        WeblabWeb.reserve_experiment(sessionid, name, category)
            .progress(handleReserveProgress)
            .fail(handleReserveFail)
            .done(function (id, time, initConfig, result) {
                console.log("RESERVATION DONE");
                console.log(result);

                $scope.experiment.reserving = false;
                $scope.reserveMessage.message = "{{ gettext('Reservation done') }}";
                $scope.reserveMessage.type = 'info';


                {# TODO: Tidy this up. #}
                {% if experiment["type"] == "js" %}

                    var params = {
                        "r": id,
                        "c": initConfig,
                        "t": time,
                        "u": WL_JSON_URL,
                        "free": "true"
                    };
                    {# //var redir = "{{ '//rawgit.com/weblabdeusto/weblabdeusto/new_client/client/src/es/deusto/weblab/public/' + experiment["html.file"] }}"; #}
                    var redir = WL_LAB_URL + "{{ experiment['config']['html.file'] }}";
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
