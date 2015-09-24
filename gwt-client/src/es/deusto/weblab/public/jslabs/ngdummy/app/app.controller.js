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
    /// Scope & Events
    /// -----------

    // Register the event handlers so that we can display the commands.
    // In a real experiment we won't actually do this, we will do whatever else.
    $scope.$on("commandSending", handleCommandSendingEvent);
    $scope.$on("commandSent", handleCommandSentEvent);


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

    function handleCommandSendingEvent(event, command) {
        $scope.ongoingCommand = command;
    }

    function handleCommandSentEvent(event, result, command, response) {
        $scope.ongoingCommand = undefined;
        $scope.lastCommandSent = command;
        $scope.lastCommandResponse = response;
    }

} // !AppController