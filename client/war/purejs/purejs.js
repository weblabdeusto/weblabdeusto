



// From StackOverflow. To extract parameters from the hash.
(function($) {
    $.QueryString = (function(a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.hash.substr(1).split('&'))
})(jQuery);




///////////////////////////////////////////////////////////////
//
// WEBLAB PSEUDO-CLASS
// The following class-like function provides the JavaScript
// API that Weblab provides to enable simple interaction for
// its experiments. The interface relies heavily on callbacks,
// to receive the events that the experiment requires to function,
// including but not limited to interaction start notifications,
// message responses, etc.
//
///////////////////////////////////////////////////////////////
Weblab = new function()
{

    ///////////////////////////////////////////////////////////////
    //
    // PRIVATE ATTRIBUTES AND FUNCTIONS
    // The API uses these internally to provide an easier to use,
    // higher level API. Users of this class do not need to be
    // aware of them.
    //
    ///////////////////////////////////////////////////////////////

    var mTargetURL;
    var mReservation;

    //! Extracts the reservation id from the URL (in the hash).
    //!
    //! @return The reservation ID if present in the URL's hash field, or undefined.
    this._extractReservation = function() {
        mReservation = $.QueryString["reservation"];
    };

    //! Extracts the targeturl from the URL (in the hash). This is the URL towards which
    //! the AJAX requests will be directed. If not specified through the URL, then
    //! it will use a default (<location>/weblab/json/).
    this._extractTargetURL = function() {
        mTargetURL = $.QueryString["targeturl"];
        if(mTargetURL == undefined)
            mTargetURL = document.location.origin + "/weblab/json/";
    };


    //! Gets the reservation that Weblab is using.
    //!
    //! @return The reservation ID.
    this._getReservation = function() {
        return mReservation;
    };

    //! Gets the TargetURL that we are using.
    //!
    //! @return The target URL.
    this._getTargetURL = function() {
        return mTargetURL;
    };


    this._poll = function() {
        var request = {"method": "poll", "params": {"reservation_id": {"id": mReservation}}};

        $.post(mTargetURL, JSON.stringify(request), function(success) {
                console.log("Data received: " + success);
                console.log(success);
            }, "json"
        );
    };

    this._get_reservation_status = function() {
        var request = {"method": "get_reservation_status", "params": {"reservation_id": {"id": mReservation}}};

        $.post(mTargetURL, JSON.stringify(request), function(success) {
                // Example of a response: {"params":{"reservation_id":{"id":"2da9363c-c5c4-4905-9f22-817cbdf1e397;2da9363c-c5c4-4905-9f22-817cbdf1e397.default-route-to-server"}}, "method":"get_reservation_status"}

                console.log("Data received: " + success);
                console.log(success);

                var result = success["result"];

                if(success["is_exception"] != false) {
                    console.error("[ERROR][get_reservation_status]: Returned exception.");
                    throw success;
                }

                var status = result["status"];

                if(status != "Reservation::confirmed") {
                    console.error("[ERROR][get_reservation_status]: Status is not Reservation::confirmed, as was expected");
                    return;
                }

                var time = result["time"];
                var starting_configuration = result["starting_configuration"];

                // TODO:QUESTION: If they are received at the same time, why are setTime and startInteraction different methods?

            }, "json"
        );
    };

    this._send_command = function(command, success, error) {
        var request = {"method": "send_command", "params": {"command": {"commandstring": command}, "reservation_id": {"id": mReservation}}};

        $.post(mTargetURL, JSON.stringify(request), function(success_data) {
                console.log("Data received: " + success_data);
                console.log(success_data);

                if(success != undefined)
                    success(success_data);
            }, "json"
        );
    };

    this._finish_experiment = function() {
        var request = {"method": "finished_experiment", "params": {"reservation_id": {"id": mReservation}}};
    }

    this._finished_experiment = function(command) {
        var request = {"method": "finished_experiment", "params": {"reservation_id": {"id": mReservation}}};

        $.post(mTargetURL, JSON.stringify(request), function(success) {
                console.log("Data received: " + success);
                console.log(success);
            }, "json"
        );
    };



    ///////////////////////////////////////////////////////////////
    //
    // PUBLIC INTERFACE
    // The following methods are part of the public interface of this
    // class. They can be used freely. Several of them rely on callbacks.
    // They might not work properly if they are run stand-alone, on a
    // context different than Weblab-Deusto.
    //
    ///////////////////////////////////////////////////////////////


    //! Sends a command to the experiment server.
    //!
    //! @param text Text of the command.
    //! @param successHandler Callback that will receive the response for the command.
    //! Takes a single string as argument.
    //! @param errorHandler Callback that will receive the response for the command.
    //! Takes a single string as argument.
    //!
    this.sendCommand = function(command, successHandler, errorHandler) {
        this.sendCommand(command, successHandler, errorHandler);
    };


    //! Sends a command to the experiment server and prints the result to console.
    //! If the command was successful it is printed to the stdout and otherwise to stderr.
    //!
    //! @param text: Command to send.
    this.testCommand = function(command) {
        this.sendCommand(command, function(success) {
            console.log("SUCCESS: " + success);
        }, function(error) {
            console.error("ERROR: " + error);
        });
    };


    //! Finishes the experiment.
    //!
    this.finishExperiment = function() {
        this._finish_experiment();
    };



    ///////////////////////////////////////////////////////////////
    //
    // CONSTRUCTOR
    // The following is internal code to create the object.
    //
    ///////////////////////////////////////////////////////////////

    // Extract the reservation id from the hash.
    this._extractReservation();

    // Extract the target URL from the hash or set a default one.
    this._extractTargetURL();

    //$.cookie("weblabsessionid", "T-Go5baSwSB3SHsO.route2");

}; // !Weblab





