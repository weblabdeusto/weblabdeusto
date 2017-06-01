angular
    .module("hwboard")
    .controller("BooleWebController", BooleWebController);



function BooleWebController($scope, $sce, $rootScope) {

    $scope.booleWebURL = $sce.trustAsResourceUrl($rootScope.BOOLEWEB);

    // ---------------
    // Implementations
    // ---------------

} // !BooleWebController
