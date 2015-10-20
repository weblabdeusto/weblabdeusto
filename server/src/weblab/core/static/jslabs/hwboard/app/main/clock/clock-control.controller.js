angular
    .module("hwboard")
    .controller("ClockControlController", ClockControlController);


function ClockControlController($scope, $log) {

    // -------------
    // Scope-related
    // -------------
    $scope.activated = false;
    $scope.runningCommand = false;
    $scope.frequency = 1000;

    $scope.isActivated = isActivated;
    $scope.activate = activate;
    $scope.deactivate = deactivate;


    // -------------
    // Implementations
    // -------------

    function isActivated() {
        return $scope.activated;
    } // !isActivated

    function activate() {
        $log.debug("Activating clock");

        $scope.runningCommand = true;


        weblab.sendCommand("ClockActivation on " + $scope.frequency)
            .done(function (response) {

                $log.debug("Clock activated");
                $scope.activated = true;
                $scope.runningCommand = false;
                $scope.$apply();
            })
            .fail(function (error) {
                $scope.activated = false;
                $scope.runningCommand = false;
                $scope.$apply();
            });
    } // !activate

    function deactivate() {
        $log.debug("Deactivating clock");

        $scope.runningCommand = true;


        weblab.sendCommand("ClockActivation off ")
            .done(function (response) {
                $log.debug("Clock deactivated");
                $scope.activated = false;
                $scope.runningCommand = false;
                $scope.$apply();
            })
            .fail(function (error) {
                $scope.activated = false;
                $scope.runningCommand = false;
                $scope.$apply();
            });

        $scope.activated = false;
    } // !deactivate

} // !ClockControlController