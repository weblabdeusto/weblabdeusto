angular
    .module("lab")
    .directive("wlExpInfo", wlExpInfo);

function wlExpInfo() {
    return {
        restrict: "E",
        scope: {
            experiment: "=",
            latestuses: "=",
            stats: "=",
            reserve: "&",
            isExperimentReserving: "&"
        },
        templateUrl: EXPINFO_TEMPLATE_URL,
    }
}
