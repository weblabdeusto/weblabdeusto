angular
    .module("hwboard")
    .controller("VirtualModelController", VirtualModelController);



function VirtualModelController($scope) {

    $scope.$on("virtualmodel-status-report", onVirtualModelStatusReport);


    // ---------------
    // Implementations
    // ---------------

    function onVirtualModelStatusReport(event, status) {
        var jqelem = $scope.getIframeElement();
        var rawelem = jqelem[0];

        // Send a message to the iframe
        rawelem.contentWindow.postMessage({message: "virtualmodel-status", data: status}, "*");
    } // !onVirtualModelStatusReport

} // !VirtualModelController