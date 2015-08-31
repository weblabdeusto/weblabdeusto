/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.experiments;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public class JSBoardBaseController implements IBoardBaseController {
	
	/*
	 * general metadata methods
	 */
	@Override
	public boolean isFacebook() {
		return isFacebookImpl();
	}

	@Override
	public void clean() {
		cleanImpl();
	}

	@Override
	public void finish() {
		finishImpl();
	}

	@Override
	public void stopPolling() {
		stopPollingImpl();
	}

	@Override
	public void disableFinishOnClose() {
		disableFinishOnCloseImpl();
	}

	/*
	 * INTERACTION METHODS
	 */
	
	@Override
	public void sendCommand(Command command) {
		sendCommandImpl(command.getCommandString(), NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}
	
	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		sendCommandImpl(command.getCommandString(), new CallbackWrapper(callback));
	}
	
	@Override
	public void sendCommand(String command) {
		sendCommandImpl(command, NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendCommand(String command, IResponseCommandCallback callback) {
		sendCommandImpl(command, new CallbackWrapper(callback));
	}

	@Override
	public void sendAsyncCommand(Command command) {
		sendAsyncCommandImpl(command.getCommandString(), NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendAsyncCommand(Command command, IResponseCommandCallback callback) {
		sendAsyncCommandImpl(command.getCommandString(), new CallbackWrapper(callback));
	}

	@Override
	public void sendAsyncCommand(String command) {
		sendAsyncCommandImpl(command, NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendAsyncCommand(String command, IResponseCommandCallback callback) {
		sendAsyncCommandImpl(command, new CallbackWrapper(callback));
	}

	@Override
	public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
		// TODO: to be implemented (file management)
		sendFileImpl("", new CallbackWrapper(callback));
	}

	@Override
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
		// TODO: to be implemented (file management)
		sendAsyncFileImpl("", new CallbackWrapper(callback));
	}
	
	/*
	 * JSNI implementations
	 * 
	 */
	public static native String getClientCodeName() /*-{
		return $wnd.gwt_experiment_config.client_code_name;
	}-*/; 
	
	public static native boolean isMobile() /*-{
		return $wnd.gwt_experiment_config.mobile;
	}-*/;
	
	public static native String getBaseLocation() /*-{
		return $wnd.gwt_experiment_config.base_location;
	}-*/;

	static native boolean isFacebookImpl() /*-{
		return $wnd.gwt_experiment_config.facebook;
	}-*/;
	
	static native void cleanImpl() /*-{
		// TODO: this is incorrect (clean != finish)
		return WebLabExp.finishExperiment();
	}-*/;

	static native void finishImpl() /*-{
		return WebLabExp.finishExperiment();
	}-*/;
	
	static native void stopPollingImpl() /*-{
		// TODO: not implemented in the current version of the JS library
	}-*/;

	static native void disableFinishOnCloseImpl() /*-{
		// TODO: not implemented in the current version of the JS library
	}-*/;
	
	static native void sendCommandImpl(String commandString, ISimpleResponseCallback callback) /*-{
		WeblabExp.sendCommand(commandString)
			.done(function(success) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onSuccess(Ljava/lang/String;)(success);
			})
			.fail(function(error) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onFailure(Ljava/lang/String;)(error);
			});
	}-*/;

	static void sendAsyncCommandImpl(String commandString, ISimpleResponseCallback callback) {
		// This method is not implemented
		sendCommandImpl(commandString, callback);
	}
	
	static native void sendFileImpl(String commandString, ISimpleResponseCallback callback) /*-{
		// TODO: integrate file management
		WeblabExp.sendCommand(commandString)
			.done(function(success) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onSuccess(Ljava/lang/String;)(success);
			})
			.fail(function(error) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onFailure(Ljava/lang/String;)(error);
			});
	}-*/;

	static void sendAsyncFileImpl(String commandString, ISimpleResponseCallback callback) {
		// This method is not implemented
		sendFileImpl(commandString, callback);
	}
}
