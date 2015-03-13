
angular
    .module("hwboard")
    .factory("statusUpdater", statusUpdater);


function statusUpdater($injector) {

    // -----------
    // Dependencies
    // -----------
    var $timeout = $injector.get("$timeout");
    var $log = $injector.get("$log");

    // -----------
    // Initialization
    // -----------

    var frequency = 2000; // How often to update.
    var _updateTimeout = undefined;

    return {
        start: start
    }; // !return


    // -----------
    // Implementations
    // -----------

    function start() {
        _updateTimeout = $timeout(updateStatus, frequency);
    }

    function updateStatus() {
        Weblab.dbgSetOfflineSendCommandResponse("programming");

        Weblab.sendCommand("STATUS", onStatusSuccess, onStatusError);
    }

    function onStatusSuccess(response) {
        $log.debug("SUCCESS: STATUS: " + response);

        _updateTimeout = $timeout(updateStatus, frequency);
    }

    function onStatusError(error) {
        $log.error("ERROR: sendCommand (status)");
        $log.error(error);

        _updateTimeout = $timeout(updateStatus, frequency);
    }

} // !statusUpdater
