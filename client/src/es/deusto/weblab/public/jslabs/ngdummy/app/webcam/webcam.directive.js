
angular
    .module("ngdummy")
    .directive("wlWebcam", wlWebcam);

function wlWebcam() {
    return {
        restrict: "E",
        scope: {
            ident: "=ident"
        },
        template: "Hello"
    }
}