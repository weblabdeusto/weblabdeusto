
angular
    .module("hwboard")
    .factory("ledUpdater", ledUpdater);


function ledUpdater($injector, $log, $timeout) {

    // -----------
    // Initialization
    // -----------

    var frequency = 2000; // How often to update.
    var _updateTimeout = undefined;
    var onLedUpdateCallback = undefined;

    // -------------
    // Declare the API
    // -------------
    return {
        start: start,
        stop: stop,
        setOnLedUpdate: setOnLedUpdate
    }; // !return


    // -----------
    // Implementations
    // -----------

    function setOnLedUpdate(callback) {
        onLedUpdateCallback = callback;
    } // !setOnLedUpdate

    function start() {
        _updateTimeout = $timeout(updateLedStatus, frequency);
    } // !start

    function stop() {
        $timeout.cancel(_updateTimeout);
    } // !stop

    function updateLedStatus() {
        Weblab.dbgSetOfflineSendCommandResponse("01010101");

        Weblab.sendCommand("READ_LEDS", onLedStatusSuccess, onLedStatusError);
    } //! updateLedStatus

    function onLedStatusSuccess(response) {
        $log.debug("SUCCESS: READ_LEDS: " + response);

        if(onLedUpdateCallback != undefined) {
            var leds = response; // String containing the status for the 8 leds.
            onLedUpdateCallback(leds)
        }

        _updateTimeout = $timeout(updateLedStatus, frequency);
    } // !onLedStatusSuccess

    function onLedStatusError(error) {
        $log.error("ERROR: sendCommand (read_leds)");
        $log.error(error);

        _updateTimeout = $timeout(updateLedStatus, frequency);
    } // !onLedStatusError

} // !ledUpdater
