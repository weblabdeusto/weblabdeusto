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

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;

class ExperimentEntry{
	
	private final ExperimentID experimentID;
	private final ExperimentCreator creator;
	private final IConfigurationRetriever configurationRetriever;
	
	public ExperimentEntry(String categoryName, String experimentName, ExperimentCreator creator, IConfigurationRetriever configurationRetriever){
		this.experimentID = new ExperimentID(new Category(categoryName), experimentName);
		this.creator = creator;
		this.configurationRetriever = configurationRetriever;
	}
	
	public IConfigurationRetriever getConfigurationRetriever(){
		return this.configurationRetriever;
	}
	
	public ExperimentID getExperimentID(){
		return this.experimentID;
	}
	
	// TODO: remove this method
	public MobileSupport getMobileSupport(){
		return this.creator.getMobileSupport();
	}
	
	// TODO: remove this method
	public final void createWeb(IBoardBaseController boardController, IExperimentLoadedCallback callback){
		this.creator.createWeb(boardController, callback);
	}
	
	// TODO: remove this method
	public final void createMobile(IBoardBaseController boardController, IExperimentLoadedCallback callback){
		this.creator.createMobile(boardController, callback);
	}
}