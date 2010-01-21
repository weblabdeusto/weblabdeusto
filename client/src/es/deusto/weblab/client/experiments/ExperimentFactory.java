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
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.exceptions.experiments.ExperimentInstanciationException;
import es.deusto.weblab.client.exceptions.experiments.ExperimentNotFoundException;
import es.deusto.weblab.client.exceptions.experiments.WlExperimentException;
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

public class ExperimentFactory {
	
	private final IConfigurationManager configurationManager;
	private final IBoardBaseController boardBaseController;
	
	public ExperimentFactory(IConfigurationManager configurationManager, IBoardBaseController boardBaseController){
		this.configurationManager = configurationManager;
		this.boardBaseController  = boardBaseController;
	}

	private boolean isSameExperiment(ExperimentID experimentID, ExperimentID other){
		return experimentID.getCategory().getCategory().equals(other.getCategory().getCategory())
			&& experimentID.getExperimentName().equals(other.getExperimentName());
	}

	public ExperimentBase experimentFactory(ExperimentID experimentID) throws WlExperimentException{
		try{
        	for(ExperimentEntry entry : EntryRegistry.entries)
        		if(this.isSameExperiment(experimentID, entry.getExperimentID()))
        			return entry.create(this.configurationManager, this.boardBaseController);
		}catch(final Exception e){
		    throw new ExperimentInstanciationException("Exception while instanciating experiment with experimentID: " + experimentID + "; reason: " + e.getMessage(), e);
		}
    	throw new ExperimentNotFoundException("Experiment " + experimentID + " not implemented in the client");
	}
}
