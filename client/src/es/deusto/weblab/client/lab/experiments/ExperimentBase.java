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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.lab.experiments;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.i18n.IWebLabI18N;
import es.deusto.weblab.client.ui.widgets.IWlWidget;

/**
 * An ExperimentBase is the abstract class from which all experiments inherit. It is 
 * basically a class with a set of methods that will be called by the controller to
 * interact. Thanks to it, the experiment dependent code does not need to handle 
 * scheduling schemas, the configuration of the experiment or the communications. 
 */
public abstract class ExperimentBase implements IWlWidget{
	
	protected final IBoardBaseController boardController;
	protected final IConfigurationRetriever configurationRetriever;
	protected static final IWebLabI18N i18n = GWT.create(IWebLabI18N.class);
	
	/**
	 * Initializes the ExperimentBase, providing the controller and the configuration retriever.
	 * 
	 * @param configurationRetriever Obtains the experiment configuration
	 * @param boardController Manages the controller, gathering information or sending commands etc.
	 */
	public ExperimentBase(IConfigurationRetriever configurationRetriever, IBoardBaseController boardController){
		this.configurationRetriever = configurationRetriever;
		this.boardController = boardController;
	}
	
	/**
	 * User selected this experiment. It can start showing the UI. It can 
	 * load the VM used (Adobe Flash, Java VM, Silverlight/Moonlight, etc.), 
	 * or define requirements of the (i.e. require 2 files, etc.). It should
	 * also show options to gather information that will be sent to the 
	 * initialization method of the experiment server, that later will be 
	 * retrieved through the {@link #getInitialData()} method. 
	 */
	public void initialize(){}
	
	/**
	 * A user, who performed the reservation outside the regular client (in
	 * a LMS or a federated environment) is going to start using this 
	 * experiment. Basically it is like the {@link #initialize()} method, 
	 * except for that it should be very fast, and take into account that no
	 * configuration can be provided (since the reservation has already been 
	 * done). 
	 */
	public void initializeReserved(){
		initialize();
	}
	
	/**
	 * Retrieves information sent to the experiment when reserving the 
	 * experiment. It might have been collected in the UI of the 
	 * {@link #initialize()} method.
	 */
	public JSONValue getInitialData(){
		return null;
	}
	
	/**
	 * User is in a queue. Thetype filter text typical behavior will be to hide the UI shown
	 * in the {@link #initialize()} method. 
	 */
	public void queued(){}
	
	/**
	 * User grabs the control of the experiment (in the server side, the 
	 * experiment is already reserved for the user).
	 * 
	 * @param time Seconds remaining. This time is the maximum permission time.
	 * @param initialConfiguration Data sent by the experiment server in the 
	 * initialization method.
	 */
	public void start(int time, String initialConfiguration){}
	
	/**
	 * User experiment session finished. The experiment should clean 
	 * its resources, or notify the user that it has finished. It may still
	 * wait for the {@link #postEnd(String)} method to be called so as to
	 * receive the information sent by the experiment when disposing 
	 * resources.
	 */
	public void end(){}
	
	private boolean endCalled = false;
	
	public final void endWrapper(){
		if(!this.endCalled){
			this.endCalled = true;
			this.end();
		}
	}
	
	/**
	 * Returns if this experiment is expecting a {@link #postEnd(String)}
	 * or not. Between {@link #end()} and {@link #postEnd(String)}, there 
	 * must be some polling to the server, especially if the experiment 
	 * server takes some time to end. However, users most of the times 
 	 * don't wait for a result, so they can start a queue somewhere else.
 	 * Other times, it is interesting to receive something at the end of 
 	 * the experiment. Those times, it is required to implement this method
 	 * returning true.  
	 * 
	 * @return if the experiment expects a {@link #postEnd(String)}
	 */
	public boolean expectsPostEnd(){
		return false;
	}
	
	/**
	 * The experiment finishes cleaning the resources in the server side. 
	 * This can be helpful when the experiment does anything in the end, 
	 * such as storing a result.
	 * 
	 * @param initialData Information sent by the server when finished the
	 * initialization of the experiment. It is the same information obtained
	 * in the {@link #start(int, String)} method, but this method will not
	 * always be called if the experiment life is too short (such as in the
	 * batch experiments).
	 * 
	 * @param endData Information sent by the server when finished cleaning
	 * resources
	 */
	public void postEnd(String initialData, String endData){
		this.boardController.clean();
	}
	
	private boolean postEndCalled = false;
	
	public final void postEndWrapper(String initialData, String endData){
		if(this.postEndCalled)
			this.boardController.clean();
		else{
			if(endData != null)
				this.postEndCalled = true;
			postEnd(initialData, endData);
		}
	}
	
	
	/**
	 * How much time does will the user have the experiment.
	 * 
	 * @param time Time in seconds remaining
	 */
	public void setTime(int time){}

	/**
	 * The method {@link #end()} should be called instead of dispose.
	 */
	@Override
	public final void dispose(){
	    this.endWrapper();
	}	
}
