angular
    .module("hwboard")
    .directive("wlTimer", wlTimer);


function wlTimer() {
    return {
        restrict: "E",
        templateUrl: "main/timer/timer.directive.html",
        controller: "TimerController",
        controllerAs: "timerController",
        link: wlTimerLink,
        scope: {
            "time": "=time"
        }
    }
} // !wlTimer


function wlTimerLink(scope, elem, attrs, ctrl) {

} // !wlTimerLink