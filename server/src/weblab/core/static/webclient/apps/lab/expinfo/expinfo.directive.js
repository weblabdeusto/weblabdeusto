angular
    .module("lab")
    .directive("wlExpInfo", wlExpInfo);

function wlExpInfo() {
    return {
        restrict: "E",
        scope: {
            experiment: "=experiment",
            latestuses: "=latestuses"
        },
        templateUrl: EXPINFO_TEMPLATE_URL
    }
}
