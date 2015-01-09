angular
    .module("lab")
    .controller("LabController", LabController);


function LabController($scope) {
    $scope.experiment = {};

    $scope.reserveInFrame = reserveInFrame;
    $scope.reserveInWindow = reserveInWindow;


    function reserveInFrame() {
    }

    function reserveInWindow() {
    }

} //! LabController
