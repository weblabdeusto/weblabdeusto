/**
 * This is the main, high-level, controller of the application.
 * We will use this controller to (among other things) set the
 * Weblab initialization and termination callbacks.
 */

angular
    .module("ngdummy")
    .controller("AppController", AppController);


function AppController($scope, $injector) {

    /// -----------
    /// Self-reference
    /// -----------
    var controller = this;

    /// -----------
    /// Dependencies
    /// -----------
    var $log = $injector.get("$log");

    /// -----------
    /// Controller methods etc
    /// -----------

    /// -----------
    /// Weblab-specific handlers for start and end
    /// -----------

    Weblab.setOnStartInteractionCallback = onExperimentStart;
    Weblab.setOnEndCallback = onExperimentEnd;

    /// -----------
    /// Implementations
    /// -----------

    function onExperimentStart(initialConfig) {
        $log.info("[EXPERIMENT START]. Initial config:");
        $log.info(initialConfig);
    }


    function onExperimentEnd() {
        $log.info("[EXPERIMENT END]");
    }

} // !AppController