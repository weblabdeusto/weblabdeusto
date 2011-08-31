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
package es.deusto.weblab.client.lab.experiments;

import com.google.gwt.json.client.JSONValue;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
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
	 * Retrieves information sent to the experiment when reserving the 
	 * experiment. It might have been collected in the UI of the 
	 * {@link #initialize()} method.
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
	
	/**
	 * The experiment finishes cleaning the resources in the server side. 
	 * This can be helpful when the experiment does anything in the end, 
	 * such as storing a result.
	 * 
	 * @param endData Information sent by the server when finished cleaning
	 * resources
	 */
	public void postEnd(String endData){}
	
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
	    this.end();
	}	
}
