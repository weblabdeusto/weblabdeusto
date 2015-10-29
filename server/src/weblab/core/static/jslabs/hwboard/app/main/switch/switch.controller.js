
angular
    .module("hwboard")
    .controller("SwitchController", SwitchController);


function SwitchController($scope, $injector, $log, $timeout) {

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

        if($scope.ongoingCommand)
            return;

        $scope.ongoingCommand = true;

        $log.debug("Switch " + $scope.ident + " pressed.");

        // Mark the button as pressed.
        $scope.isPressed = true;


        // Set the command that will be supposedly returned if we are not in weblab.
        // This is for debugging.
        // Weblab.dbgSetOfflineSendCommandResponse("ok");


        var nextStatus = $scope.isOn ? "off" : "on";

        weblab.sendCommand("ChangeSwitch " + nextStatus + " " + $scope.ident)
            .done(onCommandSentOk)
            .fail(onCommandSentFail);
    }


    /**
     * Command invoked whenever the sendCommand attempt succeeded and a response was
     * thus obtained.
     * @param response
     */
    function onCommandSentOk(response) {
        $log.debug("ChangeSwitch succeeded");

        $scope.isOn = !$scope.isOn;
        $scope.isPressed = false;
        $scope.ongoingCommand = false;

        $scope.$apply();
    }


    /**
     * Callback invoked whenever the sendCommand attempt failed.
     * @param error
     */
    function onCommandSentFail(error) {
        $log.error("SetPulse failed");

        $scope.ongoingCommand = false;
        $scope.isPressed = false;

        $scope.$apply();
    }


} // !SwitchController;