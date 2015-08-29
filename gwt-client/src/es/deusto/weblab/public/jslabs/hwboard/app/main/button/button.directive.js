
angular
    .module("hwboard")
    .directive("wlButton", wlButton);


function wlButton($injector) {
    return {
        restrict: "E",
        templateUrl: "main/button/button.directive.html",
        link: wlButtonLink,
        controller: "ButtonController",
        controllerAs: "buttonController",
        scope: {
            'ident': '@ident',
            'caption': '@caption',
            'overlay': '@overlay',
            'delay': '=delay'
        }
    };

    function wlButtonLink(scope, elem, attrs, ctrl) {

    } // !wlSwitchLink
} // !wlSwitch