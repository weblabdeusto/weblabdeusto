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

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public class JSBoardBaseController implements IBoardBaseController {
	
	private final static ISimpleResponseCallback NULL_RESPONSE_CALLBACK = new ISimpleResponseCallback() {
		@Override
		public void onFailure(String e) {
		}
		
		@Override
		public void onSuccess(String responseCommand) {
		}
	};
	
	@Override
	public void sendCommand(Command command) {
		sendCommandImpl(command.getCommandString(), NULL_RESPONSE_CALLBACK);
	}
	
	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		sendCommandImpl(command.getCommandString(), new CallbackWrapper(callback));
	}
	
	@Override
	public void sendCommand(String command) {
		sendCommandImpl(command, NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendCommand(String command, IResponseCommandCallback callback) {
		sendCommandImpl(command, new CallbackWrapper(callback));
	}

	public static native void sendCommandImpl(String commandString, ISimpleResponseCallback callback) /*-{
		WeblabExp.sendCommand(commandString)
			.done(function(success) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onSuccess(Ljava/lang/String;)(success);
			})
			.fail(function(error) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onFailure(Ljava/lang/String;)(error);
			});
	}-*/;

	@Override
	public boolean isFacebook() {
		// TODO Auto-generated method stub
		return false;
	}


	@Override
	public void sendAsyncCommand(Command command) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendAsyncCommand(Command command,
			IResponseCommandCallback callback) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendAsyncCommand(String command) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendAsyncCommand(String command,
			IResponseCommandCallback callback) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendFile(UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendAsyncFile(UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
		// TODO Auto-generated method stub

	}

	@Override
	public void clean() {
		// TODO Auto-generated method stub

	}

	@Override
	public void finish() {
		// TODO Auto-generated method stub

	}

	@Override
	public void stopPolling() {
		// TODO Auto-generated method stub

	}

	@Override
	public void disableFinishOnClose() {
		// TODO Auto-generated method stub

	}

	public final static class CallbackWrapper implements ISimpleResponseCallback {
		
		private final IResponseCommandCallback callback;
		
		public CallbackWrapper(IResponseCommandCallback callback) {
			this.callback = callback;
		}
		
		@Override
		public void onFailure(String e) {
			this.callback.onFailure(new CommException(e));
		}
		
		@Override
		public void onSuccess(String responseCommand) {
			this.callback.onSuccess(new ResponseCommand(responseCommand));
		}
	}
}
