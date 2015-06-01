'use strict'

angular
    .module('hwboard')
    .controller('MainController', MainController);


function MainController($scope, $rootScope, $injector, $log) {
    var controller = this;

    // ---------------
    // Dependencies
    // ---------------
    // For some reason when we include $log through the injector
    // but it is not as an argument, it fails.
    statusUpdater = $injector.get("statusUpdater");
    statusUpdater.setOnStatusUpdate(onStatusUpdate);

    // ---------------
    // Initialization
    // ---------------
    $log.debug("HW board experiment main controller");

    Weblab.setOnStartInteractionCallback(onStartInteraction);
    Weblab.setOnEndCallback(onEndInteraction);
    Weblab.setOnTimeCallback(onTime);

    // ---------------
    // Scope-related
    // ---------------
    $scope.time = 0;


    // ----------------
    // Implementations
    // ----------------

    function onStatusUpdate(status) {
        $log.debug("Status update: " + status);

        if( status != $scope.status) {
            $scope.status = status;

            $scope.$apply();
        }
    } // !onStatusUpdate

    function onStartInteraction(config) {
        statusUpdater.start();

        // Initialize the Virtual Model
        var command = sprintf("VIRTUALMODEL %s", $rootScope.VIRTUALMODEL);
        Weblab.sendCommand(command, onVirtualModelSetSuccess, onVirtualModelSetFailure);
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
