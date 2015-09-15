angular
    .module("lab")
    .directive("wlReserve", wlReserve);


function wlReserve() {
    return {
        restrict: "E",
        controller: "ReserveController",
        controllerAs: "reserveController",
        link: wlReserveLink,
        templateUrl: LAB_RESERVE_TEMPLATE_URL,
        scope: {
            experiment: "="
        }
    };


    function wlReserveLink(scope, elem, attrs) {
        scope.Math = Math;
    } // !wlReserveLink


} // !wlReserve
