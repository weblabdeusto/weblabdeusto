angular
    .module("lab")
    .directive("wlExpInfo", wlExpInfo);

function wlExpInfo() {
    return {
        restrict: "E",
        template: $("#expinfo-template").html()
    }
}