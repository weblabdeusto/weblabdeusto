angular
    .module("hwboard")
    .controller("ButtonController", ButtonController);


function ButtonController($scope, $injector, $log, $timeout) {

    // ----------
    // Self-reference
    // ----------
    var controller = this;

    // ----------
    // Dependencies
    // ----------

    //$log = $injector.get('$log');
    //$timeout = $injector.get('$timeout');

    // ----------
    // Scope-related
    // ----------

    $scope.button = {};
    $scope.isOn = false;
    $scope.isPressed = false;
    $scope.ongoingCommand = false;


    $scope.press = press;


    // ----------
    // Implementations
    // ----------

    /**
     * Presses the button.
     */
    function press() {

        if ($scope.ongoingCommand)
            return;

        $scope.ongoingCommand = true;

        $log.debug("Button " + $scope.ident + " pressed.");

        // Mark the button as pressed.
        $scope.isPressed = true;


        // Send command to turn it on, it will automatically turn it off after a while by sending
        // yet another command
        weblab.sendCommand("SetPulse on " + $scope.ident)
            .done(onCommandSentOk)
            .fail(onCommandSentFail);

    } // !press()


    /**
     * Command invoked when the initial sendCommand attempt succeeded and a response was
     * thus obtained.
     * @param response
     */
    function onCommandSentOk(response) {
        $log.debug("[Button] SetPulse ON");

        $scope.isOn = true;
        $scope.isPressed = false;

        // We will now send yet another command to turn it off after a while. But we will delay it a bit.

        var delay = $scope.delay;
        if (delay == undefined) {
            $log.error("[BUTTON]: Please define a button delay. Meanwhile setting it to 1000 ms");
            delay = 1000;
        }

        $timeout(function () {
            weblab.sendCommand("SetPulse off " + $scope.ident)
                .done(function (response) {
                    $log.debug("[Button] SetPulse OFF");

                    $scope.isOn = false;
                    $scope.isPressed = false;
                    $scope.ongoingCommand = false;

                    $scope.$apply();
                }).fail(function (error) {
                    $log.error("SetPulse failed (while sending button pulse)");
                    $log.error(error);

                    $scope.ongoingCommand = false;
                    $scope.isPressed = false;

                    $scope.$apply();
                });
        }, delay);


        $scope.$apply();
    }


    /**
     * Callback invoked when the initial sendCommand attempt failed.
     * @param error
     */
    function onCommandSentFail(error) {
        $log.error("SetPulse failed");

        $scope.ongoingCommand = false;
        $scope.isPressed = false;

        $scope.$apply();
    }


} // !SwitchController;