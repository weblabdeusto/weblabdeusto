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
 * WEBLAB WEB MODULE
 *
 * WeblabWeb is intended to carry the basic functions required
 * by the Weblab flask-based client to interact with the core
 * Weblab services. Thus, this library should be able to handle
 * things such as Login, Reserve or List Experiments.
 *
 * Interaction with the experiments themselves is BEYOND THE
 * SCOPE of this module.
 *
 * Requests are carried out through jQuery-powered AJAX requests.
 * By default, they will be directed to the main Weblab instance,
 * which is the one running on //www.weblab.deusto.es. However,
 * the target URLs can be modified through setTargetURLs,
 * setTargetURLsToTesting or setTargetURLsToStandard (which actually
 * just resets them to the default).
 *
 * REQUIREMENTS: jQuery
 */
WeblabWeb = new function () {

    ///////////////////////////////////////////////////////////////
    //
    // PRIVATE ATTRIBUTES AND FUNCTIONS
    // The API uses these internally to provide an easier to use,
    // higher level API. Users of this class do not need to be
    // aware of them.
    //
    ///////////////////////////////////////////////////////////////


    this.LOGIN_URL = ""; // Will be initialized through setTargetURLsToStandard.
    this.CORE_URL = ""; // Will be initialized through setTargetURLsToStandard.

    var RESERVE_POLLING_FREQ = 2000; // Number of milliseconds between polling requests.

    // For making testing possible from local files (after the various security settings
    // have been disabled).
    if(window.location != undefined) {
        if(window.location.protocol != undefined && window.location.protocol === "file:") {
            this.BASE_URL = "http:" + this.BASE_URL;
        }
    }


    /**
     * Sets the URLs to which the AJAX requests will be directed.
     * @param {str} login_url: URL of the login server (used for the login request)
     * @param {str} core_url: URL of the core server (used for most requests)
     *
     * Note that by default requests will be directed to the standard Weblab instance,
     * that is, to the Weblab instance located at //www.weblab.deusto.es/weblab. These
     * can also be explicitly reset through setTargetURLsToStandard.
     * @see setTargetURLsToStandard
     *
     * Note also that testing target URLs (for use with launch_samples.py or with the
     * test script which relies on it) can also be set easily through setTargetURLsToTesting.
     * @see setTargetURLsToTesting
     */
    this.setTargetURLs = function(login_url, core_url) {
        this.LOGIN_URL = login_url;
        this.CORE_URL = core_url;
    }

    /**
     * Sets the target URLs to the standard ones. That is, the ones that will work
     * on the main Weblab instance, which is at //www.weblab.deusto.es.
     */
    this.setTargetURLsToStandard = function() {
        this.LOGIN_URL = "//www.weblab.deusto.es/weblab/login/json/";
        this.CORE_URL = "//www.weblab.deusto.es/weblab/json/";
    }

    /**
     * Sets the target URLs to the ones that can be used for local automated testing. That is,
     * the ones that will work with a local Weblab instance started through the launch_sample
     * configuration, which is the one typically used for development.
     */
    this.setTargetURLsToTesting = function() {
        this.LOGIN_URL = "//localhost:18645/"; // As defined in the launch_sample config.
        this.CORE_URL = "//localhost:18345/"; // As defined in the launch_sample config.
    }


    // Use these functions for initialization. Standard URLs are the default.
    this.setTargetURLsToStandard();


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
     */
    this._send = function (targetURL, request) {

        var promise = $.Deferred();

        if (typeof(request) !== 'object') {
            console.error("[_SEND]: Request parameter should be an object.");
            return;
        }

        $.ajax({
            "type": "POST",
            "url": targetURL,
            "data": JSON.stringify(request),
            "dataType": "json",
            "contentType": "application/json"
        })
            .done(function (success) {
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
                promise.resolve(result);
            })
            .fail(function (fail) {
                console.error("[ERROR][_send]: Could not carry out the POST request to the target URL: " + targetURL);
                console.error(fail);

                promise.reject(fail);
            });

        return promise;

    }; // !_send


    ///////////////////////////////////////////////////////////////
    //
    // PROTECTED ATTRIBUTES AND FUNCTIONS
    // These match Weblab's API almost 1 to 1. Though they can be
    // used directly by end-users, they will generally return JSON
    // objects which will carry internal data, and they won't do much
    // else than to call the Weblab methods and return the response.
    // If an alternative public method exists, its usage is
    // recommended.
    //
    ///////////////////////////////////////////////////////////////


    /**
     * Login to the server.
     *
     * @param account: Account name.
     * @param password: Password.
     * @return: Promise. Done(sessionid) will be called if success, Fail otherwise.
     */
    this._login = function (account, password) {
        var promise = $.Deferred();

        this._send(this.LOGIN_URL,
            {
                "method": "login",
                "params": {
                    "username": account,
                    "password": password
                }
            }
        ).done(function (response) {
                // Parse the response.
                var sessionid = response["id"];
                promise.resolve(sessionid);
            }).fail(function (response) {
                promise.reject(response);
            });

        return promise;
    };

    /**
     * Retrieves information from a session's user.
     *
     * @param {string} sessionid: Session ID of the user to retrieve information about.
     * @returns Promise with .done(information) or .fail().
     */
    this._get_user_information = function (sessionid) {
        var promise = $.Deferred();

        this._send(this.CORE_URL,
            {
                "method": "get_user_information",
                "params": {
                    "session_id": {"id": sessionid}
                }
            }).done(function (response) {
                // The response by itself is a JSON-dictionary containing the information.
                promise.resolve(response);
            }).fail(function (response) {
                promise.reject(response);
            });

        return promise;
    };


    /**
     * Retrieves the list of available experiments for the user.
     *
     * @param {string} sessionid: Session ID of the user to retrieve information about.
     * @returns {Promise} With .done(information) or .fail().
     */
    this._list_experiments = function (sessionid) {
        var promise = $.Deferred();

        this._send(this.CORE_URL,
            {
                "method": "list_experiments",
                "params": {
                    "session_id": {"id": sessionid}
                }
            }).done(function (response) {
                // The response by itself is a JSON list containing the experiments.
                promise.resolve(response);
            }).fail(function (response) {
                promise.reject(response);
            });

        return promise;
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

        this._send(this.CORE_URL,
            {
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

        this._send(this.CORE_URL,
            {
                "method": "get_reservation_status",
                "params": {
                    "reservation_id": {"id": reservationid}
                }
            })
            .done(function (response) {
                // Example of a response: {"params":{"reservation_id":{"id":"2da9363c-c5c4-4905-9f22-817cbdf1e397;2da9363c-c5c4-4905-9f22-817cbdf1e397.default-route-to-server"}}, "method":"get_reservation_status"}
                console.log("Reservation status: " + response);
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
     * @returns {string} reservationid for the experiment
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
                                // The reservation has succeded. We report this as done, with the
                                // status itself.
                                promise.resolve(status);
                            }
                            else {
                                // The reservation is not ready yet. We report the status, but we will repeat
                                // the query in a couple seconds.
                                promise.notify(status);

                                // Try again soon.
                                setTimeout(check_status, RESERVE_POLLING_FREQ);
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


    ///////////////////////////////////////////////////////////////
    //
    // CONSTRUCTOR
    // The following is internal code to create the object.
    //
    ///////////////////////////////////////////////////////////////


}; // !Weblab




