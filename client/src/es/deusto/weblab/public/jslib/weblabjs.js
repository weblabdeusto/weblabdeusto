


// This is mostly so that no errors occur when executing
// the script stand-alone.
try {
    parent.wl_inst = {};
    var parent_wl_inst = parent.wl_inst;
    var external = false;
} catch(e) {
    // If can't modify the parent, fail gracefully
    var parent_wl_inst = {};
    var external = true;
}

///////////////////////////////////////////////////////////////
//
// WEBLAB PSEUDO-CLASS
// The following class-like function provides the JavaScript
// API that Weblab provides to enable simple interaction for
// its experiments. The interface relies heavily on callbacks,
// to receive the events that the experiment requires to function,
// including but not limited to interaction start notifications,
// message responses, etc.
//
///////////////////////////////////////////////////////////////
Weblab = new function () {


    ///////////////////////////////////////////////////////////////
    //
    // PRIVATE ATTRIBUTES AND FUNCTIONS
    // The API uses these internally to provide an easier to use,
    // higher level API. Users of this class do not need to be
    // aware of them.
    //
    ///////////////////////////////////////////////////////////////

    var mCommandsSentMap = {};
    var mCommandsSentCounter = 0;

    var mFilesSentMap = {};
    var mFilesSentCounter = 0;

    var mOnTimeCallback;
    var mOnEndCallback;
    var mOnFinishedCallback;
    var mOnStartInteractionCallback;
    var mOnGetInitialDataCallback;
    var mInitialConfig; // Store the initial config in case we missed the call.
    var mInitialTime; // Same thing, but for the setTime callback.

    var mDefaultFileHandlerSuccessCallback;
    var mDefaultFileHandlerErrorCallback;

    var mIsExperimentActive = false;

    // Exception thrown when trying to use a WebLab-provided function while offline.
    // (Such as when this script is used stand-alone).
    var mNotOnline = { name: "WeblabJS Error", level: "high", message: "Tried to call WebLab method. WebLab-provided methods are not available." }


    // For experiments debugging purposes. Allows fixed responses when
    // not connected to the real WebLab, thus allowing stand-alone
    // debugging of user-experiments.
    var mSendCommandDbg = false;
    var mSendCommandResponse;
    var mSendCommandResult;


    ///////////////////////////////////////////////////////////////
    //
    // INTERNAL CALLBACKS
    // Those are set on the parent's wl_inst object.
    // They are callbacks invoked by the Weblab GWT client itself.
    // Users of this class do not need to be aware of them.
    //
    ///////////////////////////////////////////////////////////////

    parent_wl_inst.version = "1.2";

    parent_wl_inst.setTime = function (time) {
        mIsExperimentActive = true;
        console.log("[DBG]: wl_inst.setTime WITH " + time);
        mInitialTime = time;
        if(mOnTimeCallback != undefined)
            mOnTimeCallback(time);
    };

    parent_wl_inst.startInteraction = function (initial_config) {
        mIsExperimentActive = true;
        mInitialConfig = initial_config; // Store the config in case setStartInteractionCallback is called late.
        if(mOnStartInteractionCallback != undefined)
            mOnStartInteractionCallback(initial_config);
    };

    parent_wl_inst.end = function () {
        mIsExperimentActive = false;
        if(mOnEndCallback != undefined)
            mOnEndCallback();
    };



    parent_wl_inst.handleCommandResponse = function (msg, id) {
        if (id in mCommandsSentMap) {
            if( mCommandsSentMap[id][0] != undefined )
                mCommandsSentMap[id][0](msg);
            delete mCommandsSentMap[id];
        }
    };

    parent_wl_inst.handleCommandError = function (msg, id) {
        if (id in mCommandsSentMap) {
            if( mCommandsSentMap[id][1] != undefined )
                mCommandsSentMap[id][1](msg);
            delete mCommandsSentMap[id];
        }
    };

    parent_wl_inst.handleFileResponse = function (msg, id) {
        if (id in mFilesSentMap) {
            mFilesSentMap[id][0](msg);
            delete mFilesSentMap[id];
        }
    };

    parent_wl_inst.handleFileError = function (msg, id) {
        if (id in mFilesSentMap) {
            mFilesSentMap[id][0](msg);
            delete mFilesSentMap[id];
        }
    };

    parent_wl_inst.getInitialData = function() {
        if(mOnGetInitialDataCallback != undefined)
            return mOnGetInitialDataCallback();
    };

    /**
     * Internally this is known as the postEnd stage. Only called sometimes.
     */
    parent_wl_inst.finished = function(finishedData) {
        if(mOnFinishedCallback != undefined)
            return mOnFinishedCallback(finishedData);
    };

    parent_wl_inst.expectsPostEnd = function() {
        return mOnFinishedCallback != undefined;
    };




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
        mCommandsSentCounter++;

        if (this.checkOnline() == false) {
            if (mSendCommandDbg)
                setTimeout(mSendCommandResult ? successHandler : errorHandler, 100, mSendCommandResponse);
            else
                throw mNotOnline;
        }
        else {
            mCommandsSentMap[mCommandsSentCounter] = [successHandler, errorHandler];
            return parent.wl_sendCommand(text, mCommandsSentCounter);
        }
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

        // A controller object so that the timeout can be stopped.
        var controller = {
            _should_stop : false,

            _active : true,

            //! Stops sending the command.
            stop : function () {this._should_stop = true;},

            //! Returns true if the command is still meant to be sent periodically.
            isActive : function() {
                return this._active;
            }
        };

        var successHandlerWrapper = function(response) {
            // Call the success handler.
            var r = successHandler(response);

            // Consider whether we need to invoke again.
            if(controller._should_stop) {
                controller._active = false;
                return;
            }

            // This method should be invoked again soon.
            if (r !== false)
                setTimeout(invokeSendCommand, time);
            else
                controller._active = false;
        }.bind(this);

        var errorHandlerWrapper = function(response) {
            // Call the error handler.
            var r = errorHandler(response);

            // Consider whether we need to invoke again.
            if(controller._should_stop) {
                controller._active = false;
                return;
            }

            // This method should be invoked again soon.
            if (r !== false)
                setTimeout(invokeSendCommand, time);
            else
                controller._active = false;
        };

        // Wrapper function to call the sendCommand itself.
        var invokeSendCommand = function() {
            this.sendCommand(text, successHandlerWrapper, errorHandlerWrapper);
        }.bind(this);

        // invokeSendCommand explicitly the first time.
        invokeSendCommand();

        // Return the controller so that it can be stopped.
        return controller;
    };


    //! Sends a command to the experiment server and prints the result to console.
    //! If the command was successful it is printed to the stdout and otherwise to stderr.
    //!
    //! @param text: Command to send.
    this.testCommand = function (text) {
        this.sendCommand(text, function(success) { console.log(success); }, function(error) { console.error(error); });
    };


    //! Sets the callback that will be invoked when the experiment finishes. Generally,
    //! an experiment finishes when it runs out of allocated time, but it may also
    //! be finished explicitly by the user or the experiment code, or by errors and
    //! and disconnections.
    //!
    this.setOnEndCallback = function (onEndCallback) {
        mOnEndCallback = onEndCallback;
    };

    //! Sets the onfinished callback, which is invoked *after* the experiment end callback is called,
    //! and which tells us that everything has been cleaned and the experiment is really over.
    //!
    this.setOnFinishedCallback = function (onFinishedCallback) {
        mOnFinishedCallback = onFinishedCallback;
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
        mDefaultFileHandlerErrorCallback = onError;
        mDefaultFileHandlerSuccessCallback = onSuccess;
    };

    //! Sets the startInteractionCallback. This is the callback that will be invoked
    //! after the Weblab experiment is successfully reserved, and the user can start
    //! interacting with the experiment. If the callback is set *after* the experiment
    //! has started, then the callback will be invoked immediately.
    //!
    //! @param onStartInteractionCallback: This callback has the prototype:
    //! onStartInteraction(initial_config). It is passed the initial configuration
    //! dictionary provided by the server.
    this.setOnStartInteractionCallback = function (onStartInteractionCallback) {
        mOnStartInteractionCallback = onStartInteractionCallback;

        // If the experiment is already active then we will call this straightaway, because
        // we probably were initialized earlier than expected. Otherwise the callback
        // would never get invoked.
        if(mIsExperimentActive)
        {
            mOnStartInteractionCallback(mInitialConfig);
        }
    };

    //! Sets the getInitialDataCallback. This is the callback that will be invoked
    //! when the reserve process is started, so the client can provide to the server
    //! whatever data it expects from the 'lobby' stage of the experiment.
    //!
    //! If the experiment is active when we call this method then the callback will be invoked, but the
    //! returned data will have no effect because other data will have been provided to the server
    //! already. Calling it is thus mostly for consistency and in case the user is interested
    //! in the event itself and not so much on returning specific data.
    //!
    //! @param onGetInitialDataCallback: This callback takes no parameters but should
    //! return the data, either as a JSON-encoded string or as an Object.
    this.setOnGetInitialDataCallback = function (onGetInitialDataCallback) {
        mOnGetInitialDataCallback = onGetInitialDataCallback;

        if(mIsExperimentActive)
        {
            // Data is purposedly ignored. The experiment is already active so no initial
            // data can be sent anymore.
            mOnGetInitialDataCallback();
        }
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
        mOnTimeCallback = onTimeCallback;

        console.log("[DBG]: SETTING ON TIME CALLBACK WITH EXP ACTIVE? " + mIsExperimentActive);
        console.log("INITIAL TIME AS: " + mInitialTime);

        if(mIsExperimentActive)
        {
            mOnTimeCallback(mInitialTime);
        }
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

    //! Retrieves a configuration property.
    //!
    //! @param name Name of the property.
    this.getProperty = function (name) {
        return parent.wl_getProperty(name);
    };

    //! Retrieves a configuration property.
    //!
    //! @param name Name of the property.
    //! @param def Default value to return if the configuration property
    //! is not found.
    this.getPropertyDef = function (name, def) {
        return parent.wl_getPropertyDef(name, def);
    };

    //! Retrieves an integer configuration property.
    //!
    //! @param name Name of the property.
    this.getIntProperty = function (name) {
        return parent.wl_getIntProperty(name);
    };

    //! Retrieves an integer configuration property.
    //!
    //! @param name Name of the property.
    //! @param def Default value to return if the configuration property
    //! is not found.
    this.getIntPropertyDef = function (name, def) {
        return parent.wl_getIntPropertyDef(name, def);
    };

    //! Finishes the experiment.
    //!
    this.clean = function () {
        return parent.wl_onClean();
    };

    //! Returns true if the experiment is active, false otherwise.
    //! An experiment is active if it has started and not finished.
    //! That is, if the server, supposedly, should be able to receive
    //! commands.
    //!
    this.isExperimentActive = function () {
        return mIsExperimentActive;
    };

    //! Checks whether this interface is actually connected to the real
    //! WebLab client.
    //!
    //! @return True, if connected to the real WL client. False otherwise.
    this.checkOnline = function () {
        if (external)
            return false;
        else
            return parent.wl_sendCommand != undefined;
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
    	parent.onFrameLoad();
    };

    //! This method is for debugging purposes. When the WeblabJS interface is used stand-alone,
    //! offline from the real Weblab client, then the response to SendCommand will be as specified.
    //!
    //! @param response Text in the response.
    //! @param result If true, SendCommand will invoke the success handler.
    //! @param result If false, SendCommand will invoke the failure handler.
    this.dbgSetOfflineSendCommandResponse = function (response, result) {
        mSendCommandDbg = true;
        mSendCommandResult = result == undefined ? true : result;
        mSendCommandResponse = response;
    }

}; //! end-of class-like Weblab function

(function() {
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

