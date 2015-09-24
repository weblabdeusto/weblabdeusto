
console.debug("Loaded the weblabexp_compat module (WeblabExp compatibility module for the old WeblabJS (v2)");


/**
 *
 * WEBLAB EXP COMPATIBILITY MODULE
 *
 * This module is meant to provide compatibility between the new WeblabExp module and the
 * old WeblabJS library.
 *
 * NOTE: Quite a few functions of the original WeblabJS are not really supported by this
 * compatibility layer. This includes some of the debugging ones.
 *
 * DEPENDENCIES: jQuery, weblabexp
 *
 *
 * Constructor.
 *
 *
 */

WeblabOld = Weblab;

Weblab = new function () {


    ///////////////////////////////////////////////////////////////
    //
    // PRIVATE ATTRIBUTES AND FUNCTIONS
    // The API uses these internally to provide an easier to use,
    // higher level API. Users of this class do not need to be
    // aware of them.
    //
    ///////////////////////////////////////////////////////////////

    var mOnTimeCallback;


    // For providing the actual functionality of this class.
    // @type : WeblabExp
    this.weblabExp = new WeblabExp();

    /**
     * Accessor for the WeblabExp object. This is obviously not part of the original WeblabJS API.
     * @returns {WeblabExp}
     */
    this.getWeblabExp = function() {
        return this.weblabExp;
    };



    ///////////////////////////////////////////////////////////////
    //
    // INTERNAL CALLBACKS
    // The compatibility class does not need internal callbacks.
    //
    ///////////////////////////////////////////////////////////////




    ///////////////////////////////////////////////////////////////
    //
    // PUBLIC INTERFACE
    // The following methods are part of the public interface of this
    // class. They can be used freely. Several of them rely on callbacks.
    // They might not work properly if they are run stand-alone, on a
    // context different than Weblab-Deusto.
    //
    ///////////////////////////////////////////////////////////////

    //! Sends a command to the experiment server.
    //!
    //! @param text Text of the command.
    //! @param successHandler Callback that will receive the response for the command.
    //! Takes a single string as argument.
    //! @param errorHandler Callback that will receive the response for the command.
    //! Takes a single string as argument.
    //!
    this.sendCommand = function (text, successHandler, errorHandler) {
        this.weblabExp.sendCommand(text)
            .done(successHandler)
            .fail(errorHandler);
    };


    //! Sends a command to the experiment server periodically.
    //! This is just an utility method.
    //! To stop the sending, you can either return "false" from any of the callbacks,
    //! or use the controller object that this method returns.
    //!
    //! When called a controller object is returned, so that the sending can be stopped
    //! at will.
    //!
    //! @param text: Text to send periodically.
    //! @param time: Time to wait after the text has been sent successfully, before sending again.
    //! @param successHandler: Success handler that will be invoked each time.
    //! @param errorHandler: Error handler that will be invoked if the send fails.
    //! @return: A controller. It supports two methods: stop(), to stop it; and isActive(), to check
    //! whether it is still running.
    this.sendCommandPeriodically = function (text, time, successHandler, errorHandler) {

        // It is likely that no experiment uses this.
        throw Error("Not yet supported in the Compatibility WeblabJS");
    };



    //! Sends a command to the experiment server and prints the result to console.
    //! If the command was successful it is printed to the stdout and otherwise to stderr.
    //!
    //! @param text: Command to send.
    this.testCommand = function (text) {
        this.weblabExp.testCommand(text);
    };


    //! Sets the callback that will be invoked when the experiment finishes. Generally,
    //! an experiment finishes when it runs out of allocated time, but it may also
    //! be finished explicitly by the user or the experiment code, or by errors and
    //! and disconnections.
    //!
    this.setOnEndCallback = function (onEndCallback) {
        this.weblabExp.onFinish(onEndCallback);
    };

    //! Sets the callbacks that will be invoked by default when a sendfile request
    //! finishes. The appropriate callback specified here will be invoked if no
    //! callback was specified in the sendFile call, or if the sendFile was done
    //! from GWT itself and not through this API.
    //!
    //! @param onSuccess Callback invoked when the sendFile request succeeds. Takes
    //! the return message as argument.
    //! @param onError Callback invoked when the sendFile request fails. Takes the
    //! return message as argument.
    this.setFileHandlerCallbacks = function (onSuccess, onError) {
        throw Error("Not yet supported in the Weblab Compatiblity layer");
    };

    //! Sets the startInteractionCallback. This is the callback that will be invoked
    //! after the Weblab experiment is successfully reserved, and the user can start
    //! interacting with the experiment. THIS METHOD WILL SOMETIMES NOT BE USED because
    //! if this library is injected then the callback will be set in the OLD WeblabJS
    //! library. For this reason, in the end of this script we append a custom callback
    //! that will invoke the old callback.
    //!
    //! @param onStartInteractionCallback: This callback has the prototype:
    //! onStartInteraction(initial_config). It is passed the initial configuration
    //! dictionary provided by the server.
    this.setOnStartInteractionCallback = function (onStartInteractionCallback) {
        console.debug("Registered START interaction callback");
        this.weblabExp.onStart(function(timeLeft, initialConfig){
            console.debug("INVOKING legacy START callback");
            console.debug("Initial config: " + initialConfig);
            console.debug("Time left: " + timeLeft);
            onStartInteractionCallback(initialConfig);

            // Invoke the time callback too.
            if(mOnTimeCallback) {
                console.debug("INVOKING legacy TIME callback");
                console.debug("Time left: " + timeLeft);
                mOnTimeCallback(timeLeft);
            }
        });
    };

    //! Sets the setTime callback. This is the callback that Weblab invokes when it defines
    //! the time that the experiment has left. Currently, the Weblab system only invokes
    //! this once, on startup. Hence, from the moment setTime is invoked, the experiment
    //! can take for granted that that is indeed the time it has left. Unless, of course,
    //! the experiment itself chooses to finish, or the user finishes early.
    //!
    //! @param onTimeCallback The callback to invoke when Weblab sets the time left for
    //! the experiment.
    //!
    this.setOnTimeCallback = function (onTimeCallback) {
        // This will be invoked from the startInteraction (that's how it works in the new WeblabExp).
        mOnTimeCallback = onTimeCallback;
    };

    //! Sets the three Weblab callbacks at once.
    //!
    //! @param onStartInteraction Start Interaction callback.
    //! @param onTime On Time callback.
    //! @param onEnd On End callback.
    //!
    //! @see setOnStartInteraction
    //! @see setOnTimeCallback
    //! @see setOnEndCallback
    this.setCallbacks = function (onStartInteraction, onTime, onEnd) {
        this.setOnStartInteractionCallback(onStartInteraction);
        this.setOnTimeCallback(onTime);
        this.setOnEndCallback(onEnd);
    };

    //! Finishes the experiment.
    //!
    this.clean = function () {
        this.weblabExp.finishExperiment();
    };

    //! Returns true if the experiment is active, false otherwise.
    //! An experiment is active if it has started and not finished.
    //! That is, if the server, supposedly, should be able to receive
    //! commands.
    //!
    this.isExperimentActive = function () {
        return this.WeblabExp.onStart().state() == "resolved" && this.WeblabExp.onFinish().state() != "resolved";
    };

    //! Checks whether this interface is actually connected to the real
    //! WebLab client.
    //!
    //! @return True, if connected to the real WL client. False otherwise.
    this.checkOnline = function () {
        // We asume always true, WeblabExp doesnt support detection or debugging yet.
        return true;
    };


    //! The GWT client will not function properly until the user's script has
    //! finished loading, because until then, callbacks might not have been set.
    //! The GWT client will know it has when the onReady()
    //! event on the iframe fires. However, sometimes, due to errors on the experiment
    //! or network, it might not fire at all.
    //! Though it is NOT required, it is possible to tell the GWT client that it has finished
    //! by using this method. Can be invoked more than once, or even if the iframe has
    //! been loaded successfully.
    this.nowLoaded = function () {
    	throw new Error("nowLoaded() is not supported by the WeblabJS compatibility layer")
    };

    //! This method is for debugging purposes. When the WeblabJS interface is used stand-alone,
    //! offline from the real Weblab client, then the response to SendCommand will be as specified.
    //!
    //! @param response Text in the response.
    //! @param result If true, SendCommand will invoke the success handler.
    //! @param result If false, SendCommand will invoke the failure handler.
    this.dbgSetOfflineSendCommandResponse = function (response, result) {
        // Failure handler not supported.
        this.weblabExp.dbgSetSendCommandResponse(response);
    }

}; //! end-of class-like Weblab function


Weblab.weblabExp.onStart().done(function(time, initialConfig) {
    console.debug("Trying to invoke TRUE LEGACY startInteraction and setTime functions, in case they were set before the compatibility layer was loaded");
    parent_wl_inst.startInteraction(initialConfig);
    parent_wl_inst.setTime(Math.round(time));
    console.debug("TRUE LEGACY invokation finished (only if they were actually set)");
});


(function() {

    console.debug("Injecting the frame resizer script")

    var script_tags = document.getElementsByTagName("script");
    var relative_path = "";
    var script_element;
    for (var i = 0; i < script_tags.length; ++i) {
        var script_src = script_tags[i].src;
        if (script_src.indexOf("weblabjs.js") >= 0) {
            relative_path = script_tags[i].src.replace("weblabjs.js", "");
            break;
        }
    }

    var new_script = document.createElement('script');
    new_script.type = 'text/javascript';
    new_script.async = true;
    new_script.src = relative_path + "weblab_iframeResizer.contentWindow.min.js";
    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(new_script, s);
})();