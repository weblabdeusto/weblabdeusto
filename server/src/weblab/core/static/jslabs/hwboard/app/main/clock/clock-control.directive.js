angular
    .module("hwboard")
    .directive("wlClockControl", wlClockControl);


function wlClockControl() {
    return {
        restrict: "E",
        controller: "ClockControlController",
        controllerAs: "clockControlController",
        templateUrl: "main/clock/clock-control.directive.html",
        link: wlClockControlLink,
        scope: {
        }
    };


    // ------------
    // Implementations
    // ------------

    function wlClockControlLink(scope, elem, attrs, ctrl) {

    } // !wlClockControlLink

} // !wlClockControl