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
import es.deusto.weblab.client.ui.BoardBase.IBoardBaseController;

public class ExperimentFactory {

	public static enum MobileSupport{
		full,
		limited,
		disabled
	}
	
	public interface IExperimentLoadedCallback{
		public void onExperimentLoaded(ExperimentBase experiment);
		public void onFailure(Throwable e);
	}
	
	private final IConfigurationManager configurationManager;
	private final IBoardBaseController boardBaseController;
	
	public ExperimentFactory(IConfigurationManager configurationManager, IBoardBaseController boardBaseController){
		this.configurationManager = configurationManager;
		this.boardBaseController  = boardBaseController;
	}

	private static boolean isSameExperiment(ExperimentID experimentID, ExperimentID other){
		return experimentID.getCategory().getCategory().equals(other.getCategory().getCategory())
			&& experimentID.getExperimentName().equals(other.getExperimentName());
	}
	
	public static MobileSupport retrieveMobileSupport(ExperimentID experimentID){
		for(ExperimentEntry entry : EntryRegistry.entries){
			if(isSameExperiment(experimentID, entry.getExperimentID()))
				return entry.getMobileSupport();
		}
		return MobileSupport.disabled;
	}

	public void experimentFactory(ExperimentID experimentID, IExperimentLoadedCallback callback, boolean forMobile){
		try{
        	for(ExperimentEntry entry : EntryRegistry.entries)
        		if(isSameExperiment(experimentID, entry.getExperimentID())){
        			if(forMobile)
        				entry.createMobile(this.configurationManager, this.boardBaseController, callback);
        			else
        				entry.createWeb(this.configurationManager, this.boardBaseController, callback);
        			return;
        		}
		}catch(final Exception e){
		    callback.onFailure(new ExperimentInstanciationException("Exception while instanciating experiment with experimentID: " + experimentID + "; reason: " + e.getMessage(), e));
		}
    	callback.onFailure(new ExperimentNotFoundException("Experiment " + experimentID + " not implemented in the client"));
	}
}
