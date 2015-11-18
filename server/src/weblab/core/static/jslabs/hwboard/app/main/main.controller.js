'use strict'

angular
    .module('hwboard')
    .controller('MainController', MainController);


function MainController($scope, $rootScope, $injector, $log) {
    var controller = this;

    // ---------------
    // Dependencies & Initialization
    // ---------------
    // For some reason when we include $log through the injector
    // but it is not as an argument, it fails.
    statusUpdater = $injector.get("statusUpdater");
    statusUpdater.setOnStatusUpdate(onStatusUpdate);

    ledUpdater = $injector.get("ledUpdater");
    ledUpdater.setOnLedUpdate(onLedUpdate);

    virtualmodelUpdater = $injector.get("virtualmodelUpdater");
    virtualmodelUpdater.setOnVirtualmodelUpdate(onVirtualmodelUpdate);

    $log.debug("HW board experiment main controller");

    weblab.onStart(onStartInteraction);
    weblab.onFinish(onEndInteraction);

    // Initialize the file ctrl
    weblab.sendFile("#file");


    // ---------------
    // Scope-related
    // ---------------
    $scope.time = 0;


    // ----------------
    // Implementations
    // ----------------

    /**
     * To receive a notification whenever a status update is received.
     * @param status
     */
    function onStatusUpdate(status) {
        $log.debug("Status update: " + status);

        if( status != $scope.status) {
            $scope.status = status;

            $scope.$apply();
        }
    } // !onStatusUpdate

    /**
     * To receive a notification whenever a LED update is received with the
     * status of each led.
     * @param leds String with a character for each one of the 8 LEDs.
     */
    function onLedUpdate(leds) {
        $log.debug("Led update: " + leds);
    } // !onLedUpdate

    /**
     * To receive a notification whenever a VirtualModel update is received.
     * @param virtualmodelUpdate
     */
    function onVirtualmodelUpdate(vmStatus) {
        $log.debug("Virtualmodel update: " + vmStatus);

        $scope.$broadcast("virtualmodel-status-report", vmStatus);
    } // !onVirtualmodelUpdate

    /**
     * To receive a notification whenever the interaction begins.
     * @param config
     */
    function onStartInteraction(time, config) {

        onTime(time);

        statusUpdater.start();
        ledUpdater.start();
        virtualmodelUpdater.start();

        // Initialize the Virtual Model
        var command = sprintf("VIRTUALWORLD_MODEL %s", $rootScope.VIRTUALMODEL);
        weblab.sendCommand(command)
            .done(onVirtualModelSetSuccess)
            .fail(onVirtualModelSetFailure);

    } // !onStartInteraction

    function onVirtualModelSetSuccess(response) {
        $log.debug("VirtualModel set: " + response);
    } // !onVirtualModelSetSuccess

    function onVirtualModelSetFailure(response) {
        $log.debug("VirtualModel set failure: " + response);
    } // !onVirtualModelSetFailure

    function onEndInteraction() {
        statusUpdater.stop();
        $scope.time = 0;
    } // !onEndInteraction

    function onTime(time) {
        $log.debug("TIME IS: " + time);
        $scope.time = time;
    } // !onTime

} // !MainController
