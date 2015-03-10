
angular
    .module("ngdummy")
    .directive("wlButton", wlButton);

function wlButton() {
    return {
        restrict: "E",
        scope: {
            ident: "@ident",
            value: "@value"
        },
        templateUrl: "app/button/button.directive.html",
        controller: "ButtonController",
        controllerAs: "buttonController"
    }
}