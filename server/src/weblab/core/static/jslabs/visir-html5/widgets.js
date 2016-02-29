//! Constructs a TimerManager.
//! @param timer_id: ID of the HTML tag for the timer.
TimerDisplayer = function (timer_id) {

    // Below the WARNING_THRESHOLD the value will be displayed in red.
    var WARNING_THRESHOLD = 120;

    var $timer = $("#" + timer_id);
    var _value = 0; // Value of the timer in seconds.
    var _countdownInterval = null;

    //! Hides the timer.
    //!
    this.hide = function () {
        $timer.hide();
    };

    //! Shows the timer.
    //!
    this.show = function () {
        $timer.show();
    };

    //! Starts counting down to zero automatically.
    //! @param timeChangedCallback: Callback that receives the time left as a parameter. It is called frequently
    //! but not necessarily every second. May be null.
    //! @see stopCountDown
    //!
    this.startCountDown = function (timeChangedCallback) {

        // Just in case it is already running.
        this.stopCountDown();

        _countdownInterval = setInterval(function () {
            if (_value > 0) {
                this.setTimeLeft(_value - 1);
                if (timeChangedCallback != null)
                    timeChangedCallback(_value);
            }
            else
                this.stopCountDown();
        }.bind(this), 1000);
    };

    //! Stops running the countdown.
    //! @see startCountDown
    //!
    this.stopCountDown = function () {
        if (_countdownInterval != null) {
            clearInterval(_countdownInterval);
        }
        _countdownInterval = null;
    };

    //! Updates the displayed text.
    //!
    this._updateDisplay = function () {
        var sec_num = _value;
        var hours = Math.floor(sec_num / 3600);
        var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
        var seconds = sec_num - (hours * 3600) - (minutes * 60);

        if (hours < 10) {
            hours = "0" + hours;
        }
        if (minutes < 10) {
            minutes = "0" + minutes;
        }
        if (seconds < 10) {
            seconds = "0" + seconds;
        }
        var time = hours + ':' + minutes + ':' + seconds;

        $timer.text(time);

        if (sec_num < WARNING_THRESHOLD) {
            $timer.css("color", "red");
        } else {
            $timer.css("color", "black");
        }
    };

    //! Sets the time that the timer has left.
    //! @param time New time in seconds.
    this.setTimeLeft = function (time) {
        if (time < 0)
            time = 0;

        _value = time;
        this._updateDisplay();
    }

}; // end-of TimerDisplayer
