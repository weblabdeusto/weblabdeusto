/*
* Copyright (C) 2005 onwards University of Deusto
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
	
	////////////////////////////////////
	// 
	// General information
	//
	
	/**
	 * Is the user accessing through facebook?
	 */
	public boolean isFacebook();
	
	/**
	 * What is the session id of the user? It is useful when using other type of communications, such
	 * as iframes in the LabVIEW experiment.
	 */
	public SessionID getSessionId();
	
	////////////////////////////////////
	// 
	// Sending commands
	//

	/**
	 * Send a command, don't care about the result
	 */
	public void sendCommand(Command command);
	
	/**
	 * Send a command, notify me with the result
	 */
	public void sendCommand(Command command, IResponseCommandCallback callback);
	
	/**
	 * Send a string command, don't care about the result
	 */
    public void sendCommand(String command);
    
	/**
	 * Send a string command, notify me with the result
	 */
	public void sendCommand(String command, IResponseCommandCallback callback);
	
	////////////////////////////////////
	// 
	// Sending async commands
	// 
	
	/**
	 * Send a command asynchronously (the system will perform several requests 
	 * until the command is finish; this is intended for long running commands), 
	 * don't care the result.
	 */
	public void sendAsyncCommand(Command command);
	
	/**
	 * Send a command asynchronously (the system will perform several requests 
	 * until the command is finish; this is intended for long running commands), 
	 * notify me with the result
	 */
	public void sendAsyncCommand(Command command, IResponseCommandCallback callback);
	
	/**
	 * Send a string command asynchronously (the system will perform several requests 
	 * until the command is finish; this is intended for long running commands), 
	 * don't care about the result
	 */
	public void sendAsyncCommand(String command);
	
	/**
	 * Send a string command asynchronously (the system will perform several requests 
	 * until the command is finish; this is intended for long running commands), 
	 * notify me with the result
	 */
	public void sendAsyncCommand(String command, IResponseCommandCallback callback);
	
	////////////////////////////////////
	// 
	// Sending files
	//
	
	/**
	 * Send a file, notify me with the result
	 */
	public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
	/**
	 * Send a file asynchronously, notify me with the result
	 */
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
	
	////////////////////////////////////
	// 
	// Cleaning
	// 
	
	/**
	 * Clean the experiment widgets and move to the list of experiments
	 */
	public void clean();
	
	/**
	 * Finish the experiment.
	 */
	public void finish();
	
	/**
	 * Indicate that polling is not required in this type of experiment.
	 */
	public void stopPolling();
	
	/**
	 * Avoid that closing the web page finishes the reservation. Useful when redirecting to 
	 * an external server.
	 */
	public void disableFinishOnClose();
}
