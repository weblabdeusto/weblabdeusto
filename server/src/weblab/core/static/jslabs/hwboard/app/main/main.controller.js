'use strict'

angular
    .module('hwboard')
    .controller('MainController', MainController);


function MainController($scope, $rootScope, $injector, $log) {
    var controller = this;

    // ---------------
    // Dependencies & Initialization
    // ---------------
    // For some reason when we include $log through the injector
    // but it is not as an argument, it fails.
    statusUpdater = $injector.get("statusUpdater");
    statusUpdater.setOnStatusUpdate(onStatusUpdate);

    ledUpdater = $injector.get("ledUpdater");
    ledUpdater.setOnLedUpdate(onLedUpdate);

    virtualmodelUpdater = $injector.get("virtualmodelUpdater");
    virtualmodelUpdater.setOnVirtualmodelUpdate(onVirtualmodelUpdate);

    $log.debug("HW board experiment main controller");

    weblab.onStart(onStartInteraction);
    weblab.onFinish(onEndInteraction);



    // ---------------
    // Scope-related
    // ---------------
    $scope.time = 0;

    $scope.doFileUpload = doFileUpload;


    // ----------------
    // Implementations
    // ----------------

    function doFileUpload() {

        $log.debug("Trying to read file");


        try { // Read the file content using HTML5's FileReader API
            // TODO: Make sure this is stable, consider using a wrapper.
            var inputElem = $("#file")[0];
            var file = inputElem.files[0];
            var fileReader = new FileReader();
            window.gFileReader = fileReader; // For debugging
            fileReader.onload = onFileReadLoadEven;
            fileReader.readAsBinaryString(file);
        } catch (e) {
            alert("There was an error while trying to read your file. Please, ensure that" +
                " it is valid.");
        }

        function onFileReadLoadEvent(ev) {
            var result = fileReader.result;

            $log.debug("File has been read client-side.");

            // Initialize the file ctrl
            weblab.sendFile(result)
                .done(onFileSent)
                .fail(onFileSentFail);
        } // !onFileReadLoadEvent

    } // !doFileUpload

    function onFileSent(result) {
        $log.debug("FILE SENT: " + result);
    } // !onFileSend

    function onFileSentFail(result) {
        $log.debug("FILE SENDING ERROR: " + result);

        alert("The server reported an error with your file. Please, ensure that you sent a valid file and" +
            " try again.");
    } // !onFileSendError

    /**
     * To receive a notification whenever a status update is received.
     * @param status
     */
    function onStatusUpdate(status) {
        $log.debug("Status update: " + status);

        if( status != $scope.status) {
            $scope.status = status;

            $scope.$apply();
        }
    } // !onStatusUpdate

    /**
     * To receive a notification whenever a LED update is received with the
     * status of each led.
     * @param leds String with a character for each one of the 8 LEDs.
     */
    function onLedUpdate(leds) {
        $log.debug("Led update: " + leds);
    } // !onLedUpdate

    /**
     * To receive a notification whenever a VirtualModel update is received.
     * @param virtualmodelUpdate
     */
    function onVirtualmodelUpdate(vmStatus) {
        $log.debug("Virtualmodel update: " + vmStatus);

        $scope.$broadcast("virtualmodel-status-report", vmStatus);
    } // !onVirtualmodelUpdate

    /**
     * To receive a notification whenever the interaction begins.
     * @param config
     */
    function onStartInteraction(time, config) {

        onTime(time);

        statusUpdater.start();
        ledUpdater.start();
        virtualmodelUpdater.start();

        // Initialize the Virtual Model
        var command = sprintf("VIRTUALWORLD_MODEL %s", $rootScope.VIRTUALMODEL);
        weblab.sendCommand(command)
            .done(onVirtualModelSetSuccess)
            .fail(onVirtualModelSetFailure);

    } // !onStartInteraction

    function onVirtualModelSetSuccess(response) {
        $log.debug("VirtualModel set: " + response);
    } // !onVirtualModelSetSuccess

    function onVirtualModelSetFailure(response) {
        $log.debug("VirtualModel set failure: " + response);
    } // !onVirtualModelSetFailure

    function onEndInteraction() {
        statusUpdater.stop();
        $scope.time = 0;
    } // !onEndInteraction

    function onTime(time) {
        $log.debug("TIME IS: " + time);
        $scope.time = time;
    } // !onTime

} // !MainController
