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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.lab.ui;

import es.deusto.weblab.client.dto.SessionID;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.ui.widgets.IWlWidget;

public abstract class BoardBase implements IWlWidget{
	public interface IBoardBaseController{
		
		public boolean isFacebook();
		public SessionID getSessionId();
		public void sendCommand(Command command);
		public void sendCommand(Command command, IResponseCommandCallback callback);
	        public void sendCommand(String command);
		public void sendCommand(String command, IResponseCommandCallback callback);
		
		public void sendAsyncCommand(Command command);
		public void sendAsyncCommand(Command command, IResponseCommandCallback callback);
		public void sendAsyncCommand(String command);
		public void sendAsyncCommand(String command, IResponseCommandCallback callback);
		
		public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
		public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
		public void onClean();
	}
	
	protected IBoardBaseController boardController;
	
	public BoardBase(IBoardBaseController boardController){
		this.boardController = boardController;
	}
	
	/**
	 * User selected this experiment. It can start showing the UI. It can 
	 * load the VM used (Adobe Flash, Java VM, Silverlight/Moonlight, etc.), 
	 * or define requirements of the (i.e. require 2 files, etc.). 
	 */
	public void initialize(){}
	
	/**
	 * Retrieves information sent to the experiment when reserving the 
	 * experiment. It might have been collected in the UI of the initialize
	 * method.
	 */
	public JSONValue getInitialData(){
		return null;
	}
	
	/**
	 * User is in a queue. The typical behavior will be to hide the UI shown
	 * in the {@link #initialize()} method. 
	 */
	public void queued(){}
	
	/**
	 * User grabs the control of the experiment (in the server side, the 
	 * experiment is already reserved for the user).
	 */
	@SuppressWarnings("unused")
	public void start(int time, String initialConfiguration){}
	
	/**
	 * User experiment session finished. The experiment should clean 
	 * its resources. 
	 */
	public void end(){}
	
	/**
	 * The experiment finishes cleaning the resources in the server side. 
	 * This can be helpful when the experiment does anything in the end, 
	 * such as storing a result.
	 */
	@SuppressWarnings("unused")
	public void postEnd(String endData){}
	
	/**
	 * How much time does will the user have the experiment.
	 */
	public abstract void setTime(int time);

	/**
	 * The method {@link #end()} should be called instead of dispose.
	 */
	@Override
	public final void dispose(){
	    this.end();
	}	
}
