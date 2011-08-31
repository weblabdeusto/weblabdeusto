/*
* Copyright (C) 2005-2009 University of Deusto
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

import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public interface IBoardBaseController{
	
	// Retrieving general information
	public boolean isFacebook();
	public SessionID getSessionId();
	
	// Sending commands
	public void sendCommand(Command command);
	public void sendCommand(Command command, IResponseCommandCallback callback);
    public void sendCommand(String command);
	public void sendCommand(String command, IResponseCommandCallback callback);
	
	// Sending async commands
	public void sendAsyncCommand(Command command);
	public void sendAsyncCommand(Command command, IResponseCommandCallback callback);
	public void sendAsyncCommand(String command);
	public void sendAsyncCommand(String command, IResponseCommandCallback callback);
	
	// Sending files
	public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
	
	// Cleaning
	public void clean();
}