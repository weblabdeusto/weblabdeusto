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

package es.deusto.weblab.client.experiments;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

abstract class ExperimentEntry{
	private ExperimentID experimentID;
	
	public ExperimentEntry(String categoryName, String experimentName){
		this.experimentID = new ExperimentID(new Category(categoryName), experimentName);
	}
	
	public ExperimentID getExperimentID(){
		return this.experimentID;
	}
	
	public abstract ExperimentBase create(IConfigurationManager configurationManager, IBoardBaseController boardController);
}