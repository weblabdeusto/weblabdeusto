angular
    .module("hwboard")
    .directive("wlBooleWeb", wlBooleWeb);


function wlBooleWeb() {

    return {
        restrict: "E",
        templateUrl: "main/boole-web/boole-web.directive.html",
        controller: "BooleWebController",
        controllerAs: "booleWebController",
        link: wlBooleWebLink,
        scope: {

        }
    }; // !return


    function wlBooleWebLink(scope, elem, attrs) {
        var iframeElement = elem.find("iframe");

        scope.getIframeElement = getIframeElement;


        // ------------------
        // Implementations
        // ------------------

        function getIframeElement() {
            return $(iframeElement);
        } // !getIframeElement

    } // !wlBooleWebLink

} // !wlBooleWeb
