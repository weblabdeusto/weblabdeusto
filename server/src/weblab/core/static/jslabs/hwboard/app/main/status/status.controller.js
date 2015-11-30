
angular
    .module("hwboard")
    .controller("StatusController", StatusController);


function StatusController($scope, $injector, $filter) {

    // ----------
    // Self-reference
    // ----------
    var controller = this;

    // ----------
    // Dependencies
    // ----------


    // ----------
    // Scope-related
    // ----------

    $scope.getDisplay = getDisplay;


    // ----------
    // Implementations
    // ----------

    /**
     * Builds the message to display.
     */
    function getDisplay() {
        if($scope.status == undefined) {
            return $filter("translate")("status.undefined");
        } else if($scope.status == 'not_ready') {
            return $filter("translate")("status.not.ready");
        }
        return '[STATUS: ' + $scope.status + '] ' + $scope.message
    }


} // !StatusController;