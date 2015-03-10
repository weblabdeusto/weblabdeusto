angular
    .module("ngdummy")
    .directive("wlWebcam", wlWebcam);

function wlWebcam($timeout) {
    return {
        restrict: "E",
        scope: {
            src: "@src"
        },
        templateUrl: "app/webcam/webcam.directive.html",
        controller: "WebcamController",
        controllerAs: "webcamController",
        link: webcamLink
    };

    function webcamLink(scope, elem, attrs, ctrl) {

        /// ---------------
        /// Bindings
        /// ---------------
        elem.find("img").bind("load error", handleLoadAndError);


        /// ---------------
        /// Implementations
        /// ---------------

        function handleLoadAndError() {
            ctrl.programRefresh();
        }

    } // ! webcamLink

} // !wlWebcam










