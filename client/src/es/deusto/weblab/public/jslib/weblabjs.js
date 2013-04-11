


// This is mostly so that no errors occur when executing
// the script stand-alone.
parent.wl_inst = {}

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
    var mOnStartInteractionCallback;

    var mDefaultFileHandlerSuccessCallback;
    var mDefaultFileHandlerErrorCallback;

    var mIsExperimentActive;

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

    parent.wl_inst.version = "1.1";

    parent.wl_inst.setTime = function (time) {
        mOnTimeCallback();
    }

    parent.wl_inst.startInteraction = function () {
        mIsExperimentActive = true;
        mOnStartInteractionCallback();
    }

    parent.wl_inst.end = function () {
        mIsExperimentActive = false;
        mOnEndCallback();
    }

    parent.wl_inst.handleCommandResponse = function (msg, id) {
        if (id in mCommandsSentMap) {
            mCommandsSentMap[id][0](msg);
            delete mCommandsSentMap[id];
        }
    };

    parent.wl_inst.handleCommandError = function (msg, id) {
        if (id in mCommandsSentMap) {
            mCommandsSentMap[id][1](msg);
            delete mCommandsSentMap[id];
        }
    };

    parent.wl_inst.handleFileResponse = function (msg, id) {
        if (id in mFilesSentMap) {
            mFilesSentMap[id][0](msg);
            delete mFilesSentMap[id];
        }
    };

    parent.wl_inst.handleFileError = function (msg, id) {
        if (id in mFilesSentMap) {
            mFilesSentMap[id][0](msg);
            delete mFilesSentMap[id];
        }
    }
    


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


    //! Sets the callback that will be invoked when the experiment finishes. Generally,
    //! an experiment finishes when it runs out of allocated time, but it may also 
    //! be finished explicitly by the user or the experiment code, or by errors and
    //! and disconnections.
    //!
    this.setOnEndCallback = function (onEndCallback) {
        mOnEndCallback = onEndCallback;
    }

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
    }

    //! Sets the startInteractionCallback. This is the callback that will be invoked
    //! after the Weblab experiment is successfully reserved, and the user can start
    //! interacting with the experiment. 
    this.setOnStartInteractionCallback = function (onStartInteractionCallback) {
        mOnStartInteractionCallback = onStartInteractionCallback;
    }

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
    }

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
    }

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
    }
    
    //! Checks whether this interface is actually connected to the real
    //! WebLab client. 
    //!
    //! @return True, if connected to the real WL client. False otherwise.
    this.checkOnline = function () {
        return parent.wl_sendCommand != undefined;
    }

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








