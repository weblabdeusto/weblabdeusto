
angular
    .module("hwboard")
    .factory("virtualmodelUpdater", virtualmodelUpdater);


function virtualmodelUpdater($injector, $log, $timeout) {

    // -----------
    // Initialization
    // -----------

    var frequency = 2000; // How often to update.
    var _updateTimeout = undefined;
    var onVirtualmodelUpdateCallback = undefined;

    // -------------
    // Declare the API
    // -------------
    return {
        start: start,
        stop: stop,
        setOnVirtualmodelUpdate: setOnVirtualmodelUpdate
    }; // !return


    // -----------
    // Implementations
    // -----------

    function setOnVirtualmodelUpdate(callback) {
        onVirtualmodelUpdateCallback = callback;
    } // !setOnVirtualmodelUpdate

    function start() {
        _updateTimeout = $timeout(updateVirtualmodelStatus, frequency);
    } // !start

    function stop() {
        $timeout.cancel(_updateTimeout);
    } // !stop

    function updateVirtualmodelStatus() {
        var testResponse = {
            water: 0.6,
            inputs: [1, 1],
            outputs: [0.5]
        };
        // Weblab.dbgSetOfflineSendCommandResponse(JSON.stringify(testResponse));

        weblab.sendCommand("VIRTUALWORLD_STATE")
            .done(onStateSuccess)
            .fail(onStateError);
    } // !updateVirtualmodelStatus


    function onStateSuccess(response) {
        $log.debug("SUCCESS: VM STATUS: " + response);

        if(onVirtualmodelUpdateCallback != undefined) {
            var status = JSON.parse(response); // TODO: Parse the actual response
            onVirtualmodelUpdateCallback(status);
        }

        _updateTimeout = $timeout(updateVirtualmodelStatus, frequency);
    } // !onStateSuccess

    function onStateError(error) {
        $log.error("ERROR: sendCommand (status)");
        $log.error(error);

        _updateTimeout = $timeout(updateVirtualmodelStatus, frequency);
    } // !onStateError

} // !virtualmodelUpdater
