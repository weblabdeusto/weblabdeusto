angular
    .module("hwboard")
    .controller("TimerController", TimerController);


function TimerController($scope, $injector, $interval) {
    // --------------
    // Initialization
    // --------------
    var controller = this;


    // --------------
    // Scope-related
    // --------------
    $scope.$watch("time", onTimeChanged);

    // --------------
    // Controller methods
    // --------------
    controller.startDecreasing = startDecreasing;
    controller.stopDecreasing = stopDecreasing;


    // --------------
    // Implementations
    // --------------

    function onTimeChanged(newTime, oldTime) {
        if(newTime < 0) {
            $scope.time = 0;
            return;
        }

        if(oldTime == 0) {
            controller.startDecreasing();
        }

        if(newTime == 0) {
            controller.stopDecreasing();
        }
    } // !onTimeChanged

    function decreaseTime() {
        if($scope.time > 0)
            $scope.time -= 1;
    } // !decreaseTime

    function startDecreasing() {
        $interval.cancel(controller._interval);
        controller._interval = $interval(decreaseTime, 1000);
    } // !startDecreasing

    function stopDecreasing() {
        $interval.cancel(controller._interval);
    }

}  // !TimerController