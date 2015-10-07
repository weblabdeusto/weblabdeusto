
angular
    .module("hwboard")
    .controller("StatusController", StatusController);


function StatusController($scope, $injector) {

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
            return "You need to Reserve the experiment before using it. Please, click on the Reserve button below."
        } else if($scope.status == 'not_ready') {
            return "You will probably want to upload your logic file before interacting with the board."
        }
        return '[STATUS: ' + $scope.status + '] ' + $scope.message
    }


} // !StatusController;