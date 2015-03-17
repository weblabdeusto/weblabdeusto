'use strict'

angular
    .module('hwboard')
    .controller('MainController', MainController);


function MainController($scope, $injector, $log) {
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
    }

    function onStartInteraction(config) {
        statusUpdater.start();
    } // !onStartInteraction

    function onEndInteraction() {
        statusUpdater.stop();
        $scope.time = 0;
    } // !onEndInteraction

    function onTime(time) {
        $log.debug("TIME IS: " + time);
        $scope.time = time;
    } // !onTime

} // !MainController
