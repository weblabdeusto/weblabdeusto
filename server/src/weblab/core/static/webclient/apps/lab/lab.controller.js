angular
    .module("lab", ['pascalprecht.translate'])
    .config(['$translateProvider', translateConfig])
    .controller("LabController", LabController);

function translateConfig($translateProvider) {
    $translateProvider.useSanitizeValueStrategy('escaped');
    $translateProvider.useUrlLoader(LOCALES_URL);
    $translateProvider.preferredLanguage(PREFERRED_LANGUAGE);
}

function LabController($scope, $injector, $http) {

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
    $scope.experiment.data = EXPERIMENT_DATA;
    $scope.experiment.reserving = false;
    $scope.experiment.active = false;
    
    $scope.latest_uses = {
        uses: []
    };

    $scope.experiment_iframe = {
        laburl: WL_LAB_URL,
        experiment: EXPERIMENT_DATA,
        language: PREFERRED_LANGUAGE,
        iframe_url: ""
    };

    if (CLIENT_TYPE == "js") {
        if (EXPERIMENT_DATA['config']['html.file'].indexOf('http://') == 0) {
            $scope.experiment_iframe.iframe_url = EXPERIMENT_DATA['config']['html.file'];
        } else {
            $scope.experiment_iframe.iframe_url = WL_LAB_URL + EXPERIMENT_DATA['config']['html.file'];
        }
    } else {
        $scope.experiment_iframe.iframe_url = GWT_BASE_URL;
    }

    $scope.experiment_info = {
        experiment: EXPERIMENT_DATA
    };

    $scope.reserveMessage = {
        message: '',
        translationData: {},
        type: 'info'
    };


    // -------------------------
    // Scope methods
    // -------------------------

    $scope.reserve = reserve;
    $scope.reserveInFrame = reserveInFrame;
    $scope.reserveInWindow = reserveInWindow;
    $scope.isExperimentActive = isExperimentActive;
    $scope.isExperimentReserving = isExperimentReserving;
    $scope.finishExperiment = finishExperiment;
    $scope.loadLatestUses = loadLatestUses;
    $scope.loadLabStats = loadLabStats;


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
    

    loadLatestUses();
    loadLabStats();

    // -------------------------
    // Implementations
    // -------------------------

    /*
    * Utility function that mimics Python's .zfill()
    */
    function zfill(n) {
        if (n < 10) 
            return "0" + n;
        return n;
    }


    /**
     * Called when an attempt is made to finish the current experiment.
     */
    function finishExperiment() {
        window.currentExperiment.finishExperiment();
    } // !finishExperiment

    /**
     * Checks whether the experiment is active.
     *
     * @return {bool}: True if the reserve has been done and the experiment has not finished yet. False otherwise.
     */
    function isExperimentActive() {
        return $scope.experiment.active;
    }

    /**
     * Checks whether the experiment is being reserved.
     */
    function isExperimentReserving() {
        return $scope.experiment.reserving;
    }
    
    /**
     * Loads the latest uses by the current user in the current experiment
     */
    function loadLatestUses() {
        $http.get(LATEST_USES_URL).then(function(response) {
            if (response.status == 200) {
                $scope.latest_uses.uses = response.data.uses;
                angular.forEach($scope.latest_uses.uses, function(value, key) {
                    var d = new Date(value.start_date.replace(/ /, 'T'));
                    var formatted = d.getFullYear() + "-" + zfill(d.getMonth() + 1) + "-" + zfill(d.getDate()) + " " + zfill(d.getHours()) + ":" + zfill(d.getMinutes()) + ":" + zfill(d.getSeconds());
                    value.start_date_formatted = formatted;
                });
            }
        });
    }

    /**
     * Loads the general stats
     */
    function loadLabStats() {
        $http.get(LAB_STATS_URL).then(function(response) {
            if (response.status == 200) {
                $scope.lab_stats = response.data.stats;
                if (response.data.stats.status == 'online') {
                    $scope.lab_stats.status = 'ONLINE';
                    $scope.lab_stats.status_color = 'green';
                }
            }
        });
    }

    /**
     * Handles a reserve progress update, received periodically while a reserve attempt is in progress.
     */
    function handleReserveProgress(status, position, result, broken) {
        window.currentExperiment._callOnQueue();
        if (!broken) {
            if (position != undefined) {
                if (position == 0) {
                    $scope.reserveMessage.message = "WAITING_IN_QUEUE_NEXT";
                    $scope.reserveMessage.type = 'info';
                }
                else {
                    $scope.reserveMessage.message = "WAITING_IN_QUEUE_N";
                    $scope.reserveMessage.translationData = {
                        position: position
                    };
                    $scope.reserveMessage.type = 'info';
                }

                $scope.$apply();
            }
        } else if(broken) {
            if (position != undefined) {
                if (position == 0) {
                    $scope.reserveMessage.message = "WAITING_FOR_INSTANCES_NEXT";
                    $scope.reserveMessage.type = 'danger';
                }
                else {
                    $scope.reserveMessage.message = "WAITING_FOR_INSTANCES_N";
                    $scope.reserveMessage.type = 'danger';
                }

                $scope.$apply();
            } else {
                $scope.reserveMessage.message = "WAITING_FOR_INSTANCES_N";
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
            $scope.reserveMessage.message = 'NOT_LOGGED_IN';
            $scope.reserveMessage.type = 'danger';
            setTimeout(function () {
                window.location = WL_LOGIN_URL;
            }, 1500);
        }
        else {
            $scope.reserveMessage.message = 'FAILED_TO_RESERVE';
            $scope.reserveMessage.translationData = {
                reason: error.message
            };
            $scope.reserveMessage.type = 'danger';
        }

        $scope.$apply();
    } // !handleReserveFail

    function reserve(where) {
        if (where == 'frame') {
            return reserveInFrame();
        } else if (where == 'window') {
            return reserveInWindow();
        } else {
            console.log("where must be frame or window: " + where);
        }
    }

    /**
     * Called to reserve the experiment in the frame.
     */
    function reserveInFrame() {
        var sessionid = WL_SESSION_ID;
        sessionid = sessionid.split(".", 1)[0];

        var name = EXPERIMENT_DATA['name'];
        var category = EXPERIMENT_DATA['category'];

        $scope.experiment.reserving = true;
        $scope.reserveMessage.message = "RESERVING";
        $scope.reserveMessage.type = 'info';

        var frame = $("#exp-frame")[0];
        var Wexp = frame.contentWindow.WeblabExp;

        // If wexp is undefined, then it is likely that the experiment loaded in the iframe does not actually
        // support being embedded in the weblab client. In this case, we will report a custom error.
        if(Wexp == undefined || Wexp.lastInstance == undefined) {
            var error = {
                message: "The experiment does not seem to support iframe mode", // TODO: translations
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

        WeblabWeb.reserve_experiment(sessionid, name, category)
            .progress(handleReserveProgress)
            .fail(handleReserveFail)
            .done(function (uid, time, initial_config, result) {

                console.log("Experiment now active");
                $scope.experiment.active = true;
                $scope.experiment.reserving = false;
                console.log("SETTING EXPERIMENT TO ACTIVE. SCOPE: ");
                console.log($scope.$id);

                $scope.reserveMessage.message = "RESERVATION_DONE";
                $scope.reserveMessage.type = 'info';

                var url = result["url"];
                var wexp = window.currentExperiment;
                wexp._setTargetURL(WL_JSON_URL);
                wexp._reservationReady(result["reservation_id"]["id"], result["time"], result["initial_configuration"]);

                // Listen also for a dispose, for other ui changes.
                wexp.onExperimentDeactive().done(function (f) {
                    $scope.experiment.active = false;
                    $scope.loadLatestUses();
                    $scope.loadLabStats();

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
        var sessionid = WL_SESSION_ID;
        sessionid = sessionid.split('.')[0];

        var name = EXPERIMENT_DATA['name'];
        var category = EXPERIMENT_DATA['category'];


        $scope.experiment.reserving = true;
        $scope.reserveMessage.message = "RESERVING";
        $scope.reserveMessage.type = 'info';

        WeblabWeb.reserve_experiment(sessionid, name, category)
            .progress(handleReserveProgress)
            .fail(handleReserveFail)
            .done(function (id, time, initConfig, result) {
                console.log("RESERVATION DONE");
                console.log(result);

                $scope.experiment.reserving = false;
                $scope.reserveMessage.message = "RESERVATION_DONE";
                $scope.reserveMessage.type = 'info';


                if (EXPERIMENT_DATA["type"] == "js") {

                    var params = {
                        "r": id,
                        "c": initConfig,
                        "t": time,
                        "u": WL_JSON_URL,
                        "free": "true"
                    };
                    var redir = WL_LAB_URL + EXPERIMENT_DATA['config']['html.file'];
                    redir += "?" + $.param(params);
                    console.log(redir);

                    window.location = redir;

                } else {

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

                }
            });
    } //! reserveInWindow()

} //! LabController
