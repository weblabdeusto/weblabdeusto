angular
    .module("lab")
    .directive("wlExpInfo", wlExpInfo);

function wlExpInfo() {
    return {
        restrict: "E",
        scope: {
            experiment: "=",
            latestuses: "=",
            reserve: "&",
            isExperimentReserving: "&"
        },
        templateUrl: EXPINFO_TEMPLATE_URL,
    }
}
