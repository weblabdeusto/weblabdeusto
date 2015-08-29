
angular
    .module("hwboard")
    .directive("wlStatus", wlStatus);


function wlStatus($injector) {
    return {
        restrict: "E",
        templateUrl: "main/status/status.directive.html",
        link: wlStatusLink,
        controller: "StatusController",
        controllerAs: "statusController",
        scope: {
            'status': '=status',
            'message': '=message'
        }
    };

    function wlStatusLink(scope, elem, attrs, ctrl) {

    } // !wlStatusLink
} // !wlStatus