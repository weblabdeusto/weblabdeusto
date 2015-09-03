WEBLABEXP_DEBUG = false;


// From StackOverflow. To extract parameters from the URL (not the hash)
(function ($) {
    $.QueryString = (function (a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i) {
            var p = a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'))
})(jQuery);


/**
 *
 * WEBLAB EXP MODULE
 *
 * WeblabExp is a library that provides a simple way to interact
 * with Weblab experiments.
 *
 * It supports two modes:
 *
 *  FRAME MODE: The laboratory which makes use of this module is meant to run from within the Weblab page,
 *  on an iframe. The laboratory can be loaded without a reserve, and the Weblab page notifies through the
 *  onStart() callbacks whenever the reserve succeeds.
 *
 *  FREE MODE: The laboratory which makes use of this module is meant to run on its own page. The laboratory cannot
 *  be loaded before the reserve is done (because, as of now, reserves through this API are not supported).
 *
 * The mode will be automatically guessed, though it can be forced by specifying it on the WeblabExp constructor.
 *
 * Note that this class is meant to be instanced anew for each laboratory reserve.
 *
 * It relies on jQuery-style deferred callbacks, and is thus
 * dependent on the jQuery library.
 *
 * DEPENDENCIES: jQuery
 *
 *
 * Constructor.
 *
 */
WeblabExp = function () {

    ///////////////////////////////////////////////////////////////
    //
    // PRIVATE ATTRIBUTES AND FUNCTIONS
    // The API uses these internally to provide an easier to use,
    // higher level API. Users of this class do not need to be
    // aware of them.
    //
    ///////////////////////////////////////////////////////////////

    /**
     * FRAME mode if true, FREE mode if false.
     * @type : bool
     */
    var mFrameMode;

    this.POLL_FREQUENCY = 4000; // Indicates how often we will poll once polling is started. Will not normally be changed.

    this.CORE_URL = ""; // Will be initialized through setTargetURLToStandard()

    var mConfiguration = {}; // Will be initialized on the start using the ?c=url argument
    var mReservation; // Must be set through setReservation()

    // Callback reporting that the weblab instance has been configured. If no config is provided it's also established.
    var mOnConfigLoadPromise = $.Deferred();

    // To store callbacks for the start
    var mOnStartPromise = $.Deferred();

    // To store callbacks for setting the time
    var mOnSetTimePromise = $.Deferred();

    // To store callbacks for running code when on a queue
    var mOnQueuePromise = $.Deferred();

    // For the callback
    var mOnGetInitialDataCallback;

    // To store callbacks for the end
    var mOnEndPromise = $.Deferred();

    // To store callbacks for the finish
    var mOnFinishPromise = $.Deferred();
    var mExpectsPostEnd = false;

    // To store whether the end() method has been called or not
    var mEndCalled = false;

    // To keep track of the timer and be able to cancel it easily when the experiment is explicitly finished.
    var mPollingTimer;
    
    // To keep track of whether we're now polling or not
    var mPolling = false;

    // When closing the current window, send a "finish()" message to the server (so somebody else can use the lab)
    var mFinishOnClose = true;

    // When closing, we don't want anybody to do something (e.g., callbacks being called, etc.)
    var mClosing = false;

    // Keep record of whether the experiment is active or not
    var mExperimentActive = false;
    var mOnExperimentActive = $.Deferred();
    var mOnExperimentDeactive = $.Deferred();

    // To keep track of the state of the object.
    var mStartCalled = false; // Whether the experiment is already started. (_reservationReady already called and callbacks triggered etc.

    // Debugging mode.
    // Note that debugging mode can be enabled but as of now, it can't be disabled.
    var mDebuggingMode = false;
    var mDbgSendCommandResponse;
    var mDbgSendCommandResult = true; // True success, false error.

    /**
     * Enables the debugging mode, in which commands do not really send anything to the server.
     * This is similar to the local-test mode.
     * @see: dbgSetSendCommandResponse()
     */
    this.enableDebuggingMode = function () {
        mDebuggingMode = true;

        this.sendCommand = function (command) {
            var p = $.Deferred();
            if (mDbgSendCommandResult)
                p.resolve(mDbgSendCommandResponse);
            else
                p.reject(mDbgSendCommandResponse);
            return p.promise();
        };
    };

    /**
     * Checks whether we are in debugging mode, and the sendCommands will thus be fake.
     * @returns {bool} True if the debugging mode is enabled, false otherwise.
     */
    this.isDebuggingMode = function () {
        return mDebuggingMode || this.isLocalTest();
    };

    /**
     * Sets the response that sendCommand will return in debugging mode.
     * @param {str} response: Send command response.
     * @param {bool} [result]: If true the response will be reported as a success, if false, as an error. True
     * by default.
     */
    this.dbgSetSendCommandResponse = function (response, result) {
        mDbgSendCommandResponse = response;

        if (result == undefined)
            result = true;

        mDbgSendCommandResult = result;
    };


    /**
     * Guesses the frame mode depending on the availability of the ReserveID.
     * @returns {bool}: The mode (true if frame mode).
     * @private
     */
    this._guessFrameMode = function () {
        var mode;
        mode = $.QueryString["free"] == undefined;

        console.debug("Guess Frame Mode: " + mode);

        return mode;
    };


    /**
     * Checks whether the WeblabExp instance is set to FRAME MODE.
     * @returns {bool} TRUE if the current mode is FRAME MODE. FALSE if the current mode is FREE MODE.
     */
    this.isFrameMode = function () {
        return mFrameMode;
    };


    /**
     * Meant to be called from the Weblab client itself whenever the reservation finishes, in FRAME mode,
     * to provide the actual reservation ID, once it is ready.
     * In FRAME mode it will trigger a call to the start interaction handlers.
     * In FREE mode it shouldn't be called from outside of this file.
     *
     * It should only be called once. Calling it twice should trigger an exception.
     *
     * @param {str} reservation_id: The reservation ID.
     * @param {number} time: Time left for the experiment. If not an int, it will be rounded from the float.
     * @param {object} initial_config: Initial configuration of the experiment, obtained from the confirmed reservation.
     */
    this._reservationReady = function (reservation_id, time, initial_config) {
        this.show();

        console.debug("[reservationReady] ReservationReady called");
        console.debug("Frame Mode: " + this.isFrameMode());

        if (mStartCalled == true)
            throw new Error("_reservationReady should only be called once");
        mStartCalled = true;
        mExperimentActive = true;
        mOnExperimentActive.resolve(reservation_id, time, initial_config);

        // Set the ID.
        mReservation = reservation_id;

        // Start the polling mechanism.
        this._startPolling();

        console.debug("[reservationReady] Resolving START promise on ReservationReady");
        mOnStartPromise.resolve(Math.round(time), initial_config);
        mOnSetTimePromise.resolve(Math.round(time));
    };

    /**
     * Sets the target URL to which the AJAX requests will be directed. This is the
     * URL of the Core server's JSON handler.
     * @param {str} target_url: URL of the core server.
     *
     * Note that by default requests will be directed to the standard Weblab instance,
     * that is, to the Weblab instance located at //www.weblab.deusto.es/weblab. These
     * can also be explicitly reset through setTargetURLToStandard.
     * @see setTargetURLToStandard
     *
     * Note also that testing target URL (for use with launch_samples.py or with the
     * test script which relies on it) can also be set easily through setTargetURLToTesting.
     * @see setTargetURLToTesting
     *
     * Note that if running from a local file (file:// protocol) http:// will be preppended
     * to the URLs.
     */
    this._setTargetURL = function (target_url) {
        this.CORE_URL = target_url;

        // For making testing possible from local files (after the various security settings
        // have been disabled).
        if (window.location != undefined) {
            if (window.location.protocol != undefined && window.location.protocol === "file:") {
                if (this.CORE_URL.indexOf("://") == -1)
                    this.CORE_URL = "http:" + this.CORE_URL;
            }
        }
    };

    /**
     * Sets the target URLs to the standard ones. That is, the ones that will work
     * on the main Weblab instance, which is at //www.weblab.deusto.es.
     */
    this._setTargetURLToStandard = function () {
        this.CORE_URL = "//www.weblab.deusto.es/weblab/json/";
    };

    /**
     * Sets the target URL to the one that can be used for local automated testing. That is,
     * the ones that will work with a local Weblab instance started through the launch_sample
     * configuration, which is the one typically used for development.
     */
    this._setTargetURLToTesting = function () {
        this.CORE_URL = "http://localhost:18345";
    };

    this._callOnQueue = function () {
        mOnQueuePromise.resolve();
    };

    this._getInitialData = function () {
        if(mOnGetInitialDataCallback != undefined)
            return mOnGetInitialDataCallback();
    }

    /**
    * Checks whether the experiment is apparently not linked to Weblab and thus running in a local test mode.
    * @returns {boolean}
    */
    this.isLocalTest = function() {
        // Check whether the page is an iframe. If it is, then it is not a local test.
        if ( window.location !== window.parent.location ) {
            return false;
        }

        // Check whether we are in free-mode. If we are, then this page is not a local test either.
        return !this.isFrameMode();
    };

    /**
     * Sets the reservation id to use.
     * For internal use. Does not trigger callbacks.
     *
     * @param {str} reservation_id: The reservation ID to use.
     * @private
     */
    this._setReservation = function (reservation_id) {
        mReservation = reservation_id;
    };

    /**
     * Retrieves the currently assigned reservation ID.
     * @returns {str} Reservation ID
     * @private
     */
    this._getReservation = function () {
        return mReservation;
    };


    // !!!!!!!!!!!!!!
    // AS OF NOW, RESERVATION-EXTRACTING IS NOT SUPPORTED. THESE FUNCTIONS MUST BE REVISED.
    // !!!!!!!!!!!!!!

    //! Extracts the reservation id from the URL (in the hash).
    //!
    //! @return The reservation ID if present in the URL's hash field, or undefined.
    this._extractReservation = function () {
        mReservation = $.QueryString["reservation"];
    };

    //! Extracts the targeturl from the URL (in the hash). This is the URL towards which
    //! the AJAX requests will be directed. If not specified through the URL, then
    //! it will use a default (<location>/weblab/json/).
    this._extractTargetURL = function () {
        mTargetURL = $.QueryString["targeturl"];
        if (mTargetURL == undefined)
            mTargetURL = document.location.origin + "/weblab/json/";
    };


    /**
     * Polls the server to check the status of the experiment.
     * This is a private method, intended to just poll the server and report the response.
     * The response is not acted upon. That is, even if the experiment finished, no callbacks
     * will be called (other than the response callback itself).
     *
     * @returns {$.Promise} Promise with .done(result) and .fail(error) callbacks.
     *
     * @private
     */
    this._poll = function () {
        var promise = $.Deferred();
        if (mPolling) {
            var request = {"method": "poll", "params": {"reservation_id": {"id": mReservation}}};

            this._send(request)
                .done(function (success) {

                    if(WEBLABEXP_DEBUG) {
                        console.debug("Data received: " + success);
                        console.debug(success);
                    }
                    promise.resolve(success);
                })
                .fail(function (error) {
                    promise.reject(error);
                });
        }
        return promise.promise();
    }; // !_poll


    /**
     * Starts the automatic polling mechanism, which will _poll the server repeteadly.
     * When the expeirment is over, it will automatically stop, and the finish callbacks
     * will be invoked (unless they have been invoked by an explicit finish call already).
     * @private
     */
    this._startPolling = function () {
        var frequency = this.POLL_FREQUENCY; // The polling freq might be a setting somewhere. For now it's hard-coded to 4 seconds.
        mPolling = true;

        this._poll()
            .done(function (result) {
                if (mPolling) {
                    mPollingTimer = setTimeout(this._startPolling.bind(this), frequency);
                    console.debug("POLL: " + result);
                }
            }.bind(this))
            .fail(function (error) {
                mPolling = false;
                // Presumably, the experiment has ended. We should actually check the error to make sure it's so.
                // TODO:

                // TODO: We should also add a way to retrieve the finish information. For now an empty call.
                if (!mClosing) {
                    this.finishExperiment();
                }
                /*
                    Original code:

                        if(e instanceof NoCurrentReservationException){ // "JSON:Client.NoCurrentReservation"
                            LabController.this.finishReservation();
                        } else if (e instanceof SessionNotFoundException) { // "JSON:Client.SessionNotFound"
                            LabController.this.finishReservationAndLogout();
                        } else {
                            LabController.this.sessionVariables.hideExperiment();
                            LabController.this.uimanager.onErrorAndFinishReservation(e.getMessage());
                            LabController.this.cleanExperiment();
                        }
                */

                console.debug("POLL F: " + error);
                // TODO: How are connection failures handled??? Do we consider the experiment finished?
            }.bind(this));

    }; // !_startPolling

    /**
     * Internal send function. It will send the request to the target URL.
     * Meant only for internal use. If an error occurs (network error, "is_exception" to true, or other) then
     * the exception will be printed to console, and nothing else will happen (as of now).
     *
     * @param request: The JSON-able to send. This method will not check whether the format of the JSON-able is
     * right or not. It is assumed it is. This should be a JSON-able object and NOT a JSON string.
     *
     * @return: Promise, whose .done(result_field) or .fail will be invoked depending on the success of the request.
     *
     * @private
     *
     */
    this._send = function (request) {

        var promise = $.Deferred();

        if (typeof(request) !== 'object') {
            console.error("[_SEND]: Request parameter should be an object.");
            return;
        }

        $.ajax({
            "type": "POST",
            "url": this.CORE_URL,
            "data": JSON.stringify(request),
            "dataType": "json",
            "contentType": "application/json"
        })
            .done(function (success, status, jqXHR) {
                // Example of a response: {"params":{"reservation_id":{"id":"2da9363c-c5c4-4905-9f22-817cbdf1e397;2da9363c-c5c4-4905-9f22-817cbdf1e397.default-route-to-server"}}, "method":"get_reservation_status"}

                // Check that the internal is_exception is set to false.
                if (success["is_exception"] === true) {

                    console.error("[ERROR][_send]: Returned exception (is_exception is true)");
                    console.error(success);

                    promise.reject(success);
                    return;
                }

                var result = success["result"];

                if (result == undefined) {
                    console.error("[ERROR][_send]: Response didn't contain the expected 'result' key.");
                    console.error(success);

                    promise.reject(success);
                    return;
                }

                // The request, whatever it contains, was apparently successful. We call the success handler, passing
                // the result field.
                promise.resolve(result, status, jqXHR);
            })
            .fail(function (fail) {
                console.error("[ERROR][_send]: Could not carry out the POST request to the target URL: " + this.CORE_URL);
                console.error(fail);

                promise.reject(fail);
            });

        return promise;

    }; // !_send


    /**
     * Internal method to send a command to the server.
     *
     * @param {str} command: The command to send.
     * @returns {$.Promise} Promise with .done(result) and .fail(error). Result is the "result" key within the response.
     *
     * @example
     * Example of a send_command result:
     * {"result": {"commandstring": "{\"blue\": true, \"white\": true, \"red\": true, \"yellow\": true}"}, "is_exception": false}
     *
     * @private
     */
    this._send_command = function (command) {
        var promise = $.Deferred();
        var request = {"method": "send_command", "params": {"command": {"commandstring": command}, "reservation_id": {"id": mReservation}}};
        console.log("Sending command: " + command);
        this._send(request)
            .done(function (success_data) {
                console.debug("Data received: " + success_data.commandstring);
                console.debug(success_data);
                promise.resolve(success_data);
            })
            .fail(function (error) {
                promise.reject(error);
            });

        return promise.promise();
    }; // !_send_command


    /**
     * Internal method to finish the experiment.
     *
     * @returns {$.Promise} Promise with .done(result) and .fail(error). Result is the "result" key within the response.
     *
     * @private
     */
    this._finished_experiment = function (forceCallServer) {
        // Disable the polling timer if needed.
        clearTimeout(mPollingTimer);
        mExperimentActive = false;

        var justCalledEnd = false;
        if (!mEndCalled) {
            mEndCalled = true;
            justCalledEnd = true
            mOnEndPromise.resolve();
        }

        var promise = $.Deferred();
        if (forceCallServer || justCalledEnd) {
            var request = {"method": "finished_experiment", "params": {"reservation_id": {"id": mReservation}}};

            this._send(request)
                .done(function (success_data) {
                    if (mExpectsPostEnd) {
                        this._poll_for_post_reservation()
                            .done(function() {
                                // Don't do mOnExperimentDeactive.resolve, since this is done the next time finish() is called
                                promise.resolve();
                            })
                            .fail(function(error) {
                                promise.reject(error);
                            });
                    } else {
                        promise.resolve();
                        mOnExperimentDeactive.resolve();
                    }
                }.bind(this))
                .fail(function (error) {
                    mOnExperimentDeactive.fail(error);
                    promise.reject(error);
                });

        } else { // !forceCallServer && !justCalledEnd
            // Experiment already ended: clean it!
            mOnExperimentDeactive.resolve();
            promise.resolve();
        }
        return promise.promise();
    };

    this._poll_for_post_reservation = function() {
        var promise = $.Deferred();
        
        var wait_for_post_reservation = function() {
            this._get_reservation_status(mReservation)
                    .done(function (result) {
                        var status = result['status'];
                        if (status === "Reservation::confirmed") {
                            setTimeout(wait_for_post_reservation, 500);
                        } else if (status === "Reservation::post_reservation") {
                            if (result['finished']) {
                                var initial_data = result['initial_data'];
                                var end_data = result['end_data'];
                                mOnFinishPromise.resolve(initial_data, end_data);
                                promise.resolve(initial_data, end_data);
                            } else {
                                setTimeout(wait_for_post_reservation, 400);
                            }
                        } else {
                            promise.reject({'msg': 'Unexpected post reservation message'});
                        }
                    })
                    .fail(function (error) {
                        promise.reject(error);
                    });
        }.bind(this);
        wait_for_post_reservation();
        return promise.promise();
    }

    /**
     * Set the experiment configuration
     */
    this._setConfiguration = function(configuration) {
        mConfiguration = configuration;
    }

    /**
    * Loads the initial configuration (e.g., target URL, experiment configuration, scripts to be loaded, etc.).
    * This function relies on a ?c=<configuration-url.json> parameter. If missing, the experiment will be
    * considered unconfigured (so it can be loaded but without calling the server and so on).
    */
    this._loadConfig = function () {
        if ($.QueryString["c"] !== undefined) {
            var that = this;
            var config_url = $.QueryString["c"];
            $.ajax({
                "type": "GET",
                "url": config_url,
                "dataType": "json",
            }).done(function (success, status, jqXHR) {
                that._setTargetURL(success.targetURL);
                that._setConfiguration(success.config);
                $.each(success.scripts, function(i, script_url) {
                    $.getScript(script_url);
                });
                mOnConfigLoadPromise.resolve();
            }).fail(function (fail) {
                console.error("Error loading configuration file from " + config_url);
                mOnConfigLoadPromise.resolve();
            });
        } else {
            console.log("Experiment disabled due to configuration URL missing. Provide a ?c=url parameter if you want to activate it.");
            mOnConfigLoadPromise.resolve();
        }
    };

    /**
     * Reserves an experiment.
     *
     * The valid reservation status reported are:
     *   - Reservation::waiting_confirmation
     *     @example
     *     {"result": {"status": "Reservation::waiting_confirmation", "url": "https://www.weblab.deusto.es/weblab/", "reservation_id": {"id": "7b2059fd-2267-4523-9fa7-e33e3524b875;7b2059fd-2267-4523-9fa7-e33e3524b875.route1"}}, "is_exception": false}
     *
     * @param {string} sessionid: Session ID of the user
     * @param {string} experiment_name: Experiment's name
     * @param {string} experiment_category: Experiment's category
     * @returns {object} Through the callback, the json response.
     * @example
     *      {"status": "Reservation::waiting_confirmation", "url": "https://www.weblab.deusto.es/weblab/", "reservation_id": {"id": "7b2059fd-2267-4523-9fa7-e33e3524b875;7b2059fd-2267-4523-9fa7-e33e3524b875.route1"}}
     */
    this._reserve_experiment = function (sessionid, experiment_name, experiment_category) {
        var promise = $.Deferred();

        this._send({
                "method": "reserve_experiment",
                "params": {
                    "session_id": {"id": sessionid},
                    "experiment_id": {
                        "exp_name": experiment_name,
                        "cat_name": experiment_category
                    },
                    "client_initial_data": "{}",
                    "consumer_data": "{}"
                }
            })
            .done(function (response) {
                promise.resolve(response);
            })
            .fail(function (response) {
                promise.reject(response);
            });

        return promise.promise();
    } // ! reserve_experiment

    /**
     * Retrieves the status of a reservation.
     * The valid reservation status are:
     *   - Reservation::confirmed
     *      @example
     *   - Reservation::waiting_confirmation
     *   - Reservation::waiting
     *      {"result": {"status": "Reservation::waiting", "position": 0, "reservation_id": {"id": "5d70d409-e8a7-4123-9dfd-56e321740099;5d70d409-e8a7-4123-9dfd-56e321740099.route1"}}, "is_exception": false}
     * @param {string} reservationid: ReservationID. This is provided by the call to reserve_experiment.
     * @returns {object} Through the callback, the whole JSON response, which includes the status itself.
     */
    this._get_reservation_status = function (reservationid) {
        var promise = $.Deferred();

        this._send({
                "method": "get_reservation_status",
                "params": {
                    "reservation_id": {"id": reservationid}
                }
            })
            .done(function (response) {
                // Example of a response: {"params":{"reservation_id":{"id":"2da9363c-c5c4-4905-9f22-817cbdf1e397;2da9363c-c5c4-4905-9f22-817cbdf1e397.default-route-to-server"}}, "method":"get_reservation_status"}
                // console.log("Reservation status: " + response);
                promise.resolve(response);
            })
            .fail(function (response) {
                promise.reject(response);
            });

        return promise.promise();
    }; // !_get_reservation


    ///////////////////////////////////////////////////////////////
    //
    // PUBLIC INTERFACE
    // The following methods are part of the public interface of this
    // class. They can be used freely. Several of them rely on callbacks.
    // They might not work properly if they are run stand-alone, on a
    // context different than Weblab-Deusto.
    //
    ///////////////////////////////////////////////////////////////


    /**
     * Get the experiment configuration
     */
    this.getConfiguration = function() {
        return mConfiguration;
    }

    /**
     * Stop polling
     * @public
     */
    this.stopPolling = function() {
        clearTimeout(mPollingTimer);
        mPolling = false;
    }

    /**
     * Sends a command to the experiment server.
     * @param {str} command: The command to send.
     * @returns {$.Promise} Promise with {@link sendCommand~done} and .fail(error) as callbacks.
     *
     * @example
     * this.sendCommand("TURN_LED ON")
     *   .done(function(result) {
     *      console.debug("LED IS: " + result);
     *   })
     *   .fail(function(error) {
     *      console.debug("Failed to turn LED ON". Cause: " + error);
     *   });
     */
    this.sendCommand = function (command) {

        var promise = $.Deferred();

        this._send_command(command)
            .done(function (success) {
                promise.resolve(success.commandstring);
            })
            .fail(function (error) {
                promise.reject(error);
            });

        return promise.promise();
    };

    /**
     * @callback sendCommand~done
     * @param {str} response: Response to the command
     */


    /**
     * Sends a command to the experiment server and prints the result to the console.
     * If the command was successful it will be printed to stdout and otherwise it
     * will be printed to stderr.
     *
     * @param {str} command: Command to send.
     * @returns {$.Promise} Promise with .done() and .fail() callbacks. Making use of it is optional.
     *
     * @example
     *  this.testCommand("TURN_LED ON");
     */
    this.testCommand = function (command) {

        var promise = $.Deferred();

        this.sendCommand(command)
            .done(function (success) {
                console.debug("SUCCESS: " + success);
                promise.resolve(success);
            })
            .fail(function (error) {
                console.error("ERROR: " + error);
                promise.reject(error);
            });

        return promise.promise();
    };

    /**
    * get reservation identifier. Used in GWT for example for sending files.
    */
    this.getReservationId = function () {
        return this._getReservation();
    };

    /**
    * get reservation identifier. Used in GWT for example for sending files.
    */
    this.getFileUploadUrl = function () {
        var baseUrl = this.CORE_URL.substring(0, this.CORE_URL.length - "json/".length);
        return baseUrl + "/web/upload/";
    };

    /**
     * Finishes the experiment. When the experiment is finished, the result is reported
     * through the .done() callback, but also through the standard onFinish callbacks,
     * which can be set through onFinish.
     * @see onFinish
     *
     * The .done() callback will be invoked first, and then the onFinish ones. It is also
     * possible that onFinish callbacks were already invoked because of a poll() result.
     * In that case, these callbacks would NOT be invoked, but the finishExperiment done callback
     * still would.
     *
     * @returns {$.Promise} Promise with .done and .fail callbacks.
     *
     */
    this.finishExperiment = function () {
        var promise = $.Deferred();
        this._finished_experiment(true)
            .done(function (success) {
                promise.resolve(success);
            })
            .fail(function (error) {
                promise.reject(error);
            });
        return promise.promise();
    };

    this.cleanExperiment = function () {
        var promise = $.Deferred();
        this._finished_experiment(false)
            .done(function (success) {
                promise.resolve(success)
            })
            .fail(function (error) {
                promise.reject(error);
            });
        return promise.promise();
    };

   /** 
    * Sets the getInitialDataCallback. This is the callback that will be invoked
    * when the reserve process is started, so the client can provide to the server
    * whatever data it expects from the 'lobby' stage of the experiment.
    *
    * If the experiment is active when we call this method then the callback will be invoked, but the
    * returned data will have no effect because other data will have been provided to the server
    * already. Calling it is thus mostly for consistency and in case the user is interested
    * in the event itself and not so much on returning specific data.
    *
    * @param onGetInitialDataCallback: This callback takes no parameters but should
    * return the data, either as a JSON-encoded string or as an Object.
    */
    this.setOnGetInitialDataCallback = function (onGetInitialDataCallback) {
        mOnGetInitialDataCallback = onGetInitialDataCallback;
    };

    /**
     * onStart( startHandler ) -> promise
     * onStart () -> promise
     *
     * Registers a start handler, which will be called when the experiment's interaction starts. Several start
     * handlers can be registered. Callbacks will be executed in FIFO order, as guaranteed by jQuery Deferred rules.
     * A start handler may not be specified. In that case, a jQuery Promise is returned, to which .done() callbacks
     * can be freely attached.
     *
     * @param {function} [startHandler]: The start handler function. Should receive the time left and the starting configuration.
     *
     * @returns {$.Promise} jQuery promise where the callbacks are stored. New callbacks can be attached through .done().
     */
    this.onStart = function (startHandler) {
        if (startHandler != undefined) {
            mOnStartPromise.done(startHandler);
        }
        return mOnStartPromise.promise();
    };

    /**
     * @callback startHandler
     * @param {number} timeLeft: Time left for the experiment.
     * @param {object} startingConfiguration: The starting configuration of the experiment, in JSON.
     */

    /**
     * onFinish( endHandler ) -> promise
     * onFinish () -> promise
     *
     * Registers an end handler, which will be called when the experiment's interaction ends. Several end
     * handlers can be registered. Callbacks will be executed in FIFO order, as guaranteed by jQuery Deferred rules.
     * A finish handler may not be specified. In that case, a jQuery Promise is returned, to which .done() callbacks
     * can be freely attached.
     *
     * @param {function} [startHandler]: The finish handler function.
     *
     * @returns {$.Promise} jQuery promise where the callbacks are stored. New callbacks can be attached through .done().
     */
    this.onFinish = function (finishHandler) {
        mExpectsPostEnd = true;
        if (finishHandler != undefined) {
            mOnFinishPromise.done(finishHandler.bind(this));
        }
        return mOnFinishPromise.promise();
    };

    /**
     * @callback finishHandler
     * @param {str} finishData: The data returned by the experiment after finishing.
     */

    /*
    * Events for adding events when an experiment is active or inactive
    */
    this.onExperimentActive = function(experimentActiveHandler) {
        if (experimentActiveHandler != undefined) {
            mOnExperimentActive.done(experimentActiveHandler.bind(this));
        }
        return mOnExperimentActive.promise();
    };
    this.onExperimentDeactive = function(experimentDeactiveHandler) {
        if (experimentDeactiveHandler != undefined) {
            mOnExperimentDeactive.done(experimentDeactiveHandler.bind(this));
        }
        return mOnExperimentDeactive.promise();
    };


    /**
     * onEnd( endHandler ) -> promise
     * onEnd() -> promise
     *
     * Registers an end handler, which will be called when the experiment's interaction ends. Several end
     * handlers can be registered. Callbacks will be executed in FIFO order, as guaranteed by jQuery Deferred rules.
     * A finish handler may not be specified. In that case, a jQuery Promise is returned, to which .done() callbacks
     * can be freely attached.
     *
     * @param {function} [endHandler]: The finish handler function.
     *
     * @returns {$.Promise} jQuery promise where the callbacks are stored. New callbacks can be attached through .done().
     */
    this.onEnd = function (onEndHandler) {
        if (onEndHandler != undefined) {
            mOnEndPromise.done(onEndHandler.bind(this));
        }
        return mOnEndPromise.promise();
    };

    /**
     * onSetTime( setTimeHandler ) -> promise
     *
     * @param {function} [setTimeHandler]: The set time handler function. Should receive the time left.
     *
     * @returns {$.Promise} jQuery promise where the callbacks are stored. New callbacks can be attached through .done().
     */
    this.onSetTime = function (setTimeHandler) {
        if (setTimeHandler != undefined) {
            mOnSetTimePromise.done(setTimeHandler);
        }
        return mOnSetTimePromise.promise();
    };

    /**
     * onQueue( queueHandler ) -> promise
     *
     * @param {function} [queueHandler]: The queue handler function. Does not receive any argument.
     *
     * @returns {$.Promise} jQuery promise where the callbacks are stored. New callbacks can be attached through .done().
     */
    this.onQueue = function (queueHandler) {
        if (queueHandler != undefined) {
            mOnQueuePromise.done(queueHandler);
        }
        return mOnQueuePromise.promise();
    };

    /**
     * Carries out free-mode initialization. Extracts the reservation ID, the
     * starting configuration, and the target URL, and calls the _reservationReady function.
     * @private
     */
    this._handleFreeModeInit = function () {
        // TODO, in case of Window there is still missing stuff
        console.info("[WeblabExp]: Running with FREE MODE enabled");

        var reservation = $.QueryString["r"];
        var startconfig = $.QueryString["c"];
        var url = $.QueryString["u"];
        var time = $.QueryString["t"];
        time = parseInt(time);

        this._setTargetURL(url);

        this._reservationReady(reservation, time, startconfig);
    };


    
    /**
    * Optional method. Reports whenever the configuration has been loaded and processed.
    */
    this.onConfigLoad = function(onConfigLoadHandler) {
        if (onConfigLoadHandler != undefined) {
            mOnConfigLoadPromise.done(onConfigLoadHandler);
        }
        return mOnConfigLoadPromise.promise();
    };

    /**
    * Disable that whenever the window is closed, the system sends a finishExperiment() event.
    */
    this.disableFinishOnClose = function() {
        mFinishOnClose = false;
    };

    /**
    * Show the body whenever loaded
    */
    this.show = function() {
        $("body").show();
    };

    /**
     * Reserves an experiment.
     *
     * The valid reservation status reported are:
     *   - Reservation::waiting_confirmation
     *     @example
     *     {"result": {"status": "Reservation::waiting_confirmation", "url": "https://www.weblab.deusto.es/weblab/", "reservation_id": {"id": "7b2059fd-2267-4523-9fa7-e33e3524b875;7b2059fd-2267-4523-9fa7-e33e3524b875.route1"}}, "is_exception": false}
     *     @example
     *     {"result": {"status": "Reservation::confirmed", "url": "https://www.weblab.deusto.es/weblab/", "remote_reservation_id": {"id": ""}, "time": 299.56350898742676, "initial_configuration": "{\"webcam\": \"https://www.weblab.deusto.es/webcam/proxied/pld2\", \"labels\": [\"cod1\", \"cod2\", \"cod3\", \"cod4\", \"cod5\"]}", "reservation_id": {"id": "8fefe7f3-8a8f-4a56-920c-64057d5a5701;8fefe7f3-8a8f-4a56-920c-64057d5a5701.route1"}}, "is_exception": false}
     *
     * @param {string} sessionid: Session ID of the user
     * @param {string} experiment_name: Experiment's name
     * @param {string} experiment_category: Experiment's category
     * @returns {object} Callback. It reports through .done(id, time, initial_config, result_object)  {@link reserve_experiment~done}, through .fail(error)
     * and through .progress(status, [queuePosition], result, [broken]).
     * @example
     *      {"status": "Reservation::waiting_confirmation", "url": "https://www.weblab.deusto.es/weblab/", "reservation_id": {"id": "7b2059fd-2267-4523-9fa7-e33e3524b875;7b2059fd-2267-4523-9fa7-e33e3524b875.route1"}}
     */
    this.reserve_experiment = function (sessionid, experiment_name, experiment_category) {
        var promise = $.Deferred();

        var self = this;

        this._reserve_experiment(sessionid, experiment_name, experiment_category)
            .done(function (reservationresponse) {

                var reservationid = reservationresponse["reservation_id"]["id"];

                // Check the status of our reservation.
                var check_status = function () {
                    self._get_reservation_status(reservationid)
                        .done(function (result) {
                            var status = result["status"];
                            if (status === "Reservation::confirmed") {
                                // The reservation has succeded. We report this as done, with certain variables.

                                var time = result["time"];
                                var startingconfig = result["initial_configuration"];
                                promise.resolve(reservationid, time, startingconfig, result);
                            }
                            else {
                                var frequency = 2 * 1000; // 2 seconds
                                var MAX_POLLING = 10 * 1000; // 10 seconds
                                var MIN_POLLING = 1 * 1000; // 1 second

                                if (status === "Reservation::waiting") {
                                    // The reservation is not ready yet. We are in the queue.
                                    // We report the status, but we will repeat
                                    // the query in a couple seconds.
                                    promise.notify(status, result["position"], result, false);

                                    // Between 1 second and 10, depending on the position (if there are 5 people, you can wait 5 seconds between polls).
                                    frequency = Math.min(MAX_POLLING, MIN_POLLING * (result["position"] + 1));
                                }
                                else if (status === "Reservation::waiting_instances") {
                                    // The reservation is not ready because apparently there are no instances
                                    // of the experiment. We will report our status and repeat the query in a
                                    // couple seconds.
                                    promise.notify(status, result["position"], result, true);

                                    // It is not very often that this changes, so half MAX_POLLING IS FINE
                                    frequency = MAX_POLLING / 2;
                                }
                                else if (status === "Reservation::waiting_confirmation") {
                                    // We are waiting for confirmation. Soon we will receive a
                                    // Reservation::confirmed state.
                                    promise.notify(status, undefined, result, false);
                                    frequency = 400; // 0.4 seconds; if you're next, we refresh quite often
                                }
                                else
                                {
                                    promise.notify(status, undefined, result);
                                }

                                // Try again soon.
                                setTimeout(check_status, frequency);
                            }
                        })
                        .fail(function (result) {
                            // An error occurred. We abort the whole reservation attempt.
                            // In the future, some further actions which could be considered:
                            // - If it was a connection error, it would make sense to retry.
                            // - If the error suggests that the reservation might have succeeded anyway,
                            //   maybe it would be appropriate to request a dispose().
                            promise.reject(result);
                        })
                };

                // This will call itself repeteadly if needed.
                check_status();

            })
            .fail(function (result) {
                promise.reject(result);
            });

        return promise.promise();
    }

    /**
     * @callback reserve_experiment~done
     * @param {str} reservationid: Reservation ID.
     * @param {number} time: Seconds left for the experiment.
     * @param {str} initialConfig: Initial configuration for the experiment as a string, which will typically contain JSON.
     * TODO: If it is guaranteed to contain JSON we should decode it ourselves.
     * @param {object} result: The result object itself which the server returned.
     */

    /**
     * @callback reserve_experiement~progress
     * @param {str} status: The status of the reserve. Will be Reservation::waiting if the queue position is available.
     * @param {number} [queuePosition]: The position in the waiting queue. 0 means being next. Can be undefined.
     * @param {object} result: The Result object.
     */




    ///////////////////////////////////
    // CONSTRUCTION & INITIALIZATION
    ///////////////////////////////////

    mFrameMode = this._guessFrameMode();

    // If we are in free-mode we have to handle some free-mode-specific initialization.
    if (mFrameMode == false) {
        this._handleFreeModeInit();
    }

    this._loadConfig();

    var that = this;
    $(window).bind('beforeunload', function(){
        if (mFinishOnClose && mExperimentActive) {
            mClosing = true;
            that.finishExperiment();
        }
    });


    ///////////////////////////////////////////////////////////////
    //
    // CONSTRUCTOR
    // The following is internal code called on object creation.
    //
    ///////////////////////////////////////////////////////////////

    // Always keep a reference to the last WeblabExp instance. This lets us have multiple
    // instances while at the same time granting us easy access from, for example,
    // scripts outside of the Weblab iframe. In the future maybe we should consider whether
    // supporting more than one instance really does make sense.
    WeblabExp.lastInstance = this;


}; // !WeblabExp



/////////////////////////////////
//
// STATIC-LIKE ELEMENTS
//
/////////////////////////////////

WeblabExp.VERSION = "1"; // Keep the version of the library in the prototype.

// Each time it is instanced, a reference to the last created instance will be saved in the prototype.
WeblabExp.lastInstance = undefined;

weblab = new WeblabExp();
