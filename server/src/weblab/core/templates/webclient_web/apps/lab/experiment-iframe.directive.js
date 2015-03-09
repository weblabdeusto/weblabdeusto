
angular
    .module("lab")
    .directive("wlExperimentIframe", wlExperimentIframe);


function wlExperimentIframe() {
    return {
        restrict: "E",
        template: $("#experiment-iframe-template").html()
    }

} //! wlExperimentIframe

