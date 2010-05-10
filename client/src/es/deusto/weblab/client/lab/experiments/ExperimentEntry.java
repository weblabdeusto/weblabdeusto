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

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.exceptions.WlExperimentException;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

abstract class ExperimentEntry{
	
	private final ExperimentID experimentID;
	private final MobileSupport mobileSupport;
	
	
	public ExperimentEntry(String categoryName, String experimentName, MobileSupport mobileSupport){
		this.experimentID = new ExperimentID(new Category(categoryName), experimentName);
		this.mobileSupport = mobileSupport;
	}
	
	public ExperimentID getExperimentID(){
		return this.experimentID;
	}
	
	public MobileSupport getMobileSupport(){
		return this.mobileSupport;
	}
	
	public abstract void createWeb(IConfigurationManager configurationManager, IBoardBaseController boardController, IExperimentLoadedCallback callback);
	
	// 
	// Override this method to implement a mobile user interface
	// 
	public void createMobile(IConfigurationManager configurationManager, IBoardBaseController boardController, IExperimentLoadedCallback callback){
		if(this.mobileSupport == MobileSupport.disabled)
			callback.onFailure(new WlExperimentException("Couldn't create mobile version of experiment " + this.experimentID + ": not supported"));
		else
			this.createWeb(configurationManager, boardController, callback);
	}
}