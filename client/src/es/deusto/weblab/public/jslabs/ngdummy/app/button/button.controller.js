
angular
    .module("ngdummy")
    .controller("ButtonController", ButtonController);


function ButtonController($scope, $injector) {

    // ------------------
    // Self-reference
    // ------------------
    var controller = this;

    // ------------------
    // Requirements
    // ------------------
    var log = $injector.get("$log");

    // ------------------
    // Scope
    // ------------------

    // ------------------
    // Controller methods
    // ------------------

    controller.press = press;

    // ------------------
    // Cleanup
    // ------------------

    // ------------------
    // Implementations
    // ------------------

    function press() {

        log.info("[BUTTON PRESSED]: " + $scope.ident);

        // We set the next 'debug' response. Whenever we call sendCommand from outside of Weblab,
        // which will generally be done for debugging purposes while we develop the experiment,
        // the sendCommand will return 'ok'.
        Weblab.dbgSetOfflineSendCommandResponse("ok");

        // Send the command to Weblab.
        Weblab.sendCommand("button " + $scope.ident, onCommandSuccess, onCommandError);

        function onCommandSuccess(response) {
            log.info("[BUTTON PRESSED RESPONSE]: " + response)

            // Process the response here.

        } // !onCommandSuccess

        function onCommandError(error) {
            log.error("[BUTTON PRESSED ERROR]:");
            log.error(error);

            // Handle the error here.

        } // !onCommandError

    } // !press

} // !ButtonController