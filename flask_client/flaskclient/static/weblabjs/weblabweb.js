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


///////////////////////////////////////////////////////////////
//
// WEBLAB WEB MODULE
//
// WeblabWeb is intended to carry the basic functions required
// by the Weblab flask-based client to interact with the core
// Weblab services. Thus, this library should be able to handle
// things such as Login, Reserve or List Experiments.
//
// Interaction with the experiments themselves is BEYOND THE
// SCOPE of this module.
//
// REQUIREMENTS: jQuery
//
///////////////////////////////////////////////////////////////
WeblabWeb = new function () {

        ///////////////////////////////////////////////////////////////
        //
        // PRIVATE ATTRIBUTES AND FUNCTIONS
        // The API uses these internally to provide an easier to use,
        // higher level API. Users of this class do not need to be
        // aware of them.
        //
        ///////////////////////////////////////////////////////////////

        var BASE_URL = "//www.weblab.deusto.es/weblab";


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

            $.post(targetURL, JSON.stringify(request), function (success) {
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
                }, "json"
            ).fail(function (fail) {
                    console.error("[ERROR][_send]: Could not carry out the POST request to the target URL: " + targetURL);
                    console.error(fail);

                    promise.reject(fail);
                });

            return promise;

        }; // !_send


        /**
         * Login to the server.
         *
         * @param account: Account name.
         * @param password: Password.
         * @return: Promise. Done(sessionid) will be called if success, Fail otherwise.
         */
        this._login = function (account, password) {
            var promise = $.Deferred();

            this._send(BASE_URL + "/login/json/",
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

            this._send(BASE_URL + "/json/",
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

            this._send(BASE_URL + "/json/",
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
         * @returns {string} reservationid for the experiment
         * @example
         *      {"status": "Reservation::waiting_confirmation", "url": "https://www.weblab.deusto.es/weblab/", "reservation_id": {"id": "7b2059fd-2267-4523-9fa7-e33e3524b875;7b2059fd-2267-4523-9fa7-e33e3524b875.route1"}}
         */
        this._reserve_experiment = function (sessionid, experiment_name, experiment_category) {
            var promise = $.Deferred();

            this._send(BASE_URL + "/json",
                {
                    "method": "reserve_experiment",
                    "params": {
                        "session_id": {"id": sessionid},
                        "experiment_id": {
                            "exp_name": experiment_name,
                            "cat_name": experiment_category
                        }
                    }
                })
                .done(function (response) {
                    promise.resolve(response);
                })
                .fail(function (response) {
                    promise.reject(response);
                });
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
         * @returns {object} The whole JSON response, which includes the status itself.
         */
        this._get_reservation_status = function (reservationid) {
            var promise = $.Deferred();

            this._send(BASE_URL + "/json",
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


        ///////////////////////////////////////////////////////////////
        //
        // CONSTRUCTOR
        // The following is internal code to create the object.
        //
        ///////////////////////////////////////////////////////////////


    }; // !Weblab




