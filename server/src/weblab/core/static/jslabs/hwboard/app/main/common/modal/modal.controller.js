
angular
    .module("hwboard")
    .controller("ModalController", ModalController);


function ModalController($scope, $uibModalInstance, params) {
    var vm = this;

    $scope.params = params;


    $scope.ok = function() {
        $uibModalInstance.close();
    };

    $scope.cancel = function() {
        $uibModalInstance.dismiss("cancel");
    };
} // !ModalController