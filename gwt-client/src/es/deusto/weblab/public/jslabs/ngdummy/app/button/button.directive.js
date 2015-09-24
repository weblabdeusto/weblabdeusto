/**
 * Defines the wl-button directive, which provides some very simple weblab-oriented
 * buttons. Whenever clicked they will send a "button {ident}" command to weblab.
 */

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


