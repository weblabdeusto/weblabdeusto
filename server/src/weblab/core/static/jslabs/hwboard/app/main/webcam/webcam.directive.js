/**
 * Defines the wl-webcam directive, which provides an automatically-refreshing webcam.
 * It is very easy to use. It can be added to the DOM as such:
 * <wl-webcam src="http://myimg.jpg"></wl-webcam>
 */


angular
    .module("hwboard")
    .directive("wlWebcam", wlWebcam);


function wlWebcam() {
    return {
        restrict: "E",
        scope: {
            src: "@src"
        },
        templateUrl: "main/webcam/webcam.directive.html",
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










