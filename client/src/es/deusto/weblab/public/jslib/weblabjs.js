


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
        mOnStartInteractionCallback();
    }

    parent.wl_inst.end = function () {
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

    this.sendCommand = function (text, successHandler, errorHandler) {
        mCommandsSentCounter++;
        mCommandsSentMap[mCommandsSentCounter] = [successHandler, errorHandler];
        return parent.wl_sendCommand(text, mCommandsSentCounter);
    };


    this.setOnEndCallback = function (onEndCallback) {
        mOnEndCallback = onEndCallback;
    }

    this.setOnStartInteractionCallback = function (onStartInteractionCallback) {
        mOnStartInteractionCallback = onStartInteractionCallback;
    }

    this.setOnTimeCallback = function (onTimeCallback) {
        mOnTimeCallback = onTimeCallback;
    }

    this.setCallbacks = function (onStartInteraction, onTime, onEnd) {
        this.setOnStartInteractionCallback(onStartInteraction);
        this.setOnTimeCallback(onTime);
        this.setOnEndCallback(onEnd);
    }

    this.getProperty = function (name) {
        return parent.wl_getProperty(name);
    };

    this.getPropertyDef = function (name, def) {
        return parent.wl_getPropertyDef(name, def);
    };

    this.getIntProperty = function (name) {
        return parent.wl_getIntProperty(name);
    };

    this.getIntPropertyDef = function (name, def) {
        return parent.wl_getIntPropertyDef(name, def);
    };

    this.clean = function () {
        return parent.wl_onClean();
    };

}; //! end-of class-like Weblab function








