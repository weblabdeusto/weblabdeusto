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

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.ui.widgets.IWlWidget;

public abstract class BoardBase implements IWlWidget{
	public interface IBoardBaseController{
		public boolean isFacebook();
	    public void sendCommand(Command command);
		public void sendCommand(Command command, IResponseCommandCallback callback);
	    public void sendCommand(String command);
		public void sendCommand(String command, IResponseCommandCallback callback);
		public void sendFile(UploadStructure uploadStructure, IResponseCommandCallback callback);
		public void onClean();
	}
	
	protected IBoardBaseController boardController;
	
	public BoardBase(IBoardBaseController boardController){
		this.boardController = boardController;
	}
	
	/*
	 * WebLab will call this method when the user selects this experiment.
	 * The purpose of this method is to load the VM used (Adobe Flash, Java VM,
	 * Silverlight/Moonlight, etc.), and to define what requirements the 
	 * experiment needs (i.e. it will require 2 files, etc.). 
	 */
	public void initialize(){}
	
	/*
	 * WebLab wil call this method when the user is in a queue. The typical
	 * behaviour will be to hidden. 
	 */
	public void queued(){}
	
	/*
	 * WebLab will call this method as soon as the user grabs the control of
	 * the experiment (in the server side, the experiment is already reserved
	 * for the user).
	 */
	public abstract void start(int time, String initialConfiguration);
	
	/*
	 * WebLab will call this method as soon as the user session finishes. The
	 * experiment should clean its resources. 
	 */
	public abstract void end();
	
	/*
	 * WebLab will call this method to tell how much time does will the user have
	 * the experiment.
	 */
	public abstract void setTime(int time);

	// The method "end" should be called instead of dispose.
	@Override
	public final void dispose(){
	    this.end();
	}	
}
