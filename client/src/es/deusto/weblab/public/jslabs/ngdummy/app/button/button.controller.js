
angular
    .module("ngdummy")
    .controller("ButtonController", ButtonController);


function ButtonController($scope, $injector) {

    // ------------------
    // Self-reference
    // ------------------
    var controller = this;

    // ------------------
    // Requirements
    // ------------------
    var log = $injector.get("$log");

    // ------------------
    // Scope
    // ------------------

    // ------------------
    // Controller methods
    // ------------------

    controller.press = press;

    // ------------------
    // Cleanup
    // ------------------

    // ------------------
    // Implementations
    // ------------------

    function press() {
        log.info("[BUTTON PRESSED]: " + $scope.ident);
    }

} // !ButtonController