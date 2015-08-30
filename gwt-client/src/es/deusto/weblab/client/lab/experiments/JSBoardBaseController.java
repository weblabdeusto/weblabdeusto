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

	@Override
	public boolean isFacebook() {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public void sendCommand(Command command) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendCommand(String command) {
		// TODO Auto-generated method stub

	}

	@Override
	public void sendCommand(String command, IResponseCommandCallback callback) {
		// TODO Auto-generated method stub

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
}
