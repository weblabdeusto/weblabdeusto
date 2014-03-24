

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


Weblab = new function()
{
    var mTargetUrl = "http://localhost/weblab/json/";
    var mReservation;

    //! Extracts the reservation id from the URL (in the hash).
    //!
    //! @return The reservation ID if present in the URL's hash field, or undefined.
    this._extractReservation = function() {
        mReservation = $.QueryString["reservation"];
    };

    //! Gets the reservation that Weblab is using.
    //!
    //! @return The reservation ID.
    this.getReservation = function() {
        return mReservation;
    };

    this._poll = function() {
        var request = {"method": "poll", "params": {"reservation_id": {"id": mReservation}}};

        $.post(mTargetUrl, JSON.stringify(request), function(success) {
                console.log("Data received: " + success);
                console.log(success);
            }, "json"
        );
    };

    this._get_reservation_status = function() {
        var request = {"method": "get_reservation_status", "params": {"reservation_id": {"id": mReservation}}};

        $.post(mTargetUrl, JSON.stringify(request), function(success) {
                console.log("Data received: " + success);
                console.log(success);
            }, "json"
        );
    };

    this._send_command = function(command) {
        var request = {"method": "send_command", "params": {"command": {"commandstring": command}, "reservation_id": {"id": mReservation}}};

        $.post(mTargetUrl, JSON.stringify(request), function(success) {
                console.log("Data received: " + success);
                console.log(success);
            }, "json"
        );
    };

    this._finished_experiment = function(command) {
        var request = {"method": "finished_experiment", "params": {"reservation_id": {"id": mReservation}}};

        $.post(mTargetUrl, JSON.stringify(request), function(success) {
                console.log("Data received: " + success);
                console.log(success);
            }, "json"
        );
    }


    this._extractReservation();
};





