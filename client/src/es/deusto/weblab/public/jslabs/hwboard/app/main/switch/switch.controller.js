
angular
    .module("hwboard")
    .controller("SwitchController", SwitchController);


function SwitchController($scope, $injector) {

    // ----------
    // Self-reference
    // ----------
    var controller = this;

    // ----------
    // Dependencies
    // ----------

    $log = $injector.get('$log');
    $timeout = $injector.get('$timeout');

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

        $log.debug("Button " + $scope.ident + " pressed.");

        // Mark the button as pressed.
        $scope.isPressed = true;


        // Set the command that will be supposedly returned if we are not in weblab.
        // This is for debugging.
        Weblab.dbgSetOfflineSendCommandResponse("ok");


        var nextStatus = $scope.isOn ? "off" : "on";

        Weblab.sendCommand("SetPulse " + nextStatus + " " + $scope.ident,
            onCommandSentOk, onCommandSentFail);
    }


    /**
     * Command invoked whenever the sendCommand attempt succeeded and a response was
     * thus obtained.
     * @param response
     */
    function onCommandSentOk(response) {
        $log.debug("SetPulse succeeded");

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

        $scope.$apply();
    }


} // !SwitchController;