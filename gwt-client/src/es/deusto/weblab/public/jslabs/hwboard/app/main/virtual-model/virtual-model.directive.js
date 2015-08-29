angular
    .module("hwboard")
    .directive("wlVirtualModel", wlVirtualModel);


function wlVirtualModel() {

    return {
        restrict: "E",
        templateUrl: "main/virtual-model/virtual-model.directive.html",
        controller: "VirtualModelController",
        controllerAs: "virtualModelController",
        link: wlVirtualModelLink,
        scope: {

        }
    }; // !return


    function wlVirtualModelLink(scope, elem, attrs) {
        var iframeElement = elem.find("iframe");

        scope.getIframeElement = getIframeElement;


        // ------------------
        // Implementations
        // ------------------

        function getIframeElement() {
            return $(iframeElement);
        } // !getIframeElement

    } // !wlVirtualModelLink

} // !wlVirtualModel