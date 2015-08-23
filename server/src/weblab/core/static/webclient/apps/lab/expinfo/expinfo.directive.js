angular
    .module("lab")
    .directive("wlExpInfo", wlExpInfo);

function wlExpInfo() {
    return {
        restrict: "E",
        scope: {
            experiment: "=experiment"
        },
        templateUrl: EXPINFO_TEMPLATE_URL
    }
}
