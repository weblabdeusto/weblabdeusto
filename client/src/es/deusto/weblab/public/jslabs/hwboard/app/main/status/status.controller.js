
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

    $log = $injector.get('$log');
    $timeout = $injector.get('$timeout');

    // ----------
    // Scope-related
    // ----------


    // ----------
    // Implementations
    // ----------


} // !StatusController;