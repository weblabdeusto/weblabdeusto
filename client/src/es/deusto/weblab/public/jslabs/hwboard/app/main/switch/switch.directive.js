
angular
    .module("hwboard")
    .directive("wlSwitch", wlSwitch);


function wlSwitch($injector) {
    return {
        restrict: "E",
        templateUrl: "main/switch/switch.directive.html",
        link: wlSwitchLink,
        controller: "SwitchController",
        controllerAs: "switchController",
        scope: {
            'ident': '@ident',
            'caption': '@caption',
            'overlay': '@overlay'
        }
    };

    function wlSwitchLink(scope, elem, attrs, ctrl) {

    } // !wlSwitchLink
} // !wlSwitch