angular
    .module("hwboard")
    .directive("wlVirtualModel", wlVirtualModel);


function wlVirtualModel() {

    return {
        restrict: "E",
        templateUrl: "main/virtual-model/virtual-model.directive.html",
        controller: "VirtualModelController",
        controllerAs: "virtualModelController",
        scope: {

        }
    }; // !return

} // !wlVirtualModel