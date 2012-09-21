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

import java.util.HashSet;
import java.util.Set;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentCreatorInstanciationException;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentInstanciationException;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentNotFoundException;

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
	
	private final IBoardBaseController boardBaseController;
	
	public ExperimentFactory(IBoardBaseController boardBaseController){
		this.boardBaseController  = boardBaseController;
	}

	private static boolean isSameExperiment(ExperimentID experimentID, ExperimentID other){
		return experimentID.getCategory().getCategory().equals(other.getCategory().getCategory())
			&& experimentID.getExperimentName().equals(other.getExperimentName());
	}
	
	public static MobileSupport retrieveMobileSupport(ExperimentID experimentID){
		for(final ExperimentEntry entry : EntryRegistry.entries){
			if(ExperimentFactory.isSameExperiment(experimentID, entry.getExperimentID()))
				return entry.getMobileSupport();
		}
		return MobileSupport.disabled;
	}

	public void experimentFactory(ExperimentID experimentID, IExperimentLoadedCallback callback, boolean forMobile){
		try{
        	for(final ExperimentEntry entry : EntryRegistry.entries)
        		if(ExperimentFactory.isSameExperiment(experimentID, entry.getExperimentID())){
        			if(forMobile)
        				entry.createMobile(this.boardBaseController, callback);
        			else
        				entry.createWeb(this.boardBaseController, callback);
        			return;
        		}
		}catch(final Exception e){
		    callback.onFailure(new ExperimentInstanciationException("Exception while instanciating experiment with experimentID: " + experimentID + "; reason: " + e.getMessage(), e));
		}
    	callback.onFailure(new ExperimentNotFoundException("Experiment " + experimentID + " not implemented in the client"));
	}
	
	public static void loadExperiments(IConfigurationManager configurationManager) throws InvalidConfigurationValueException, ConfigurationKeyNotFoundException{
		final Set<String> alreadyTriedCreatorFactories = new HashSet<String>();
		final Set<String> alreadyRegisteredExperiments = new HashSet<String>();
		
		try{
			for(IExperimentCreatorFactory creatorFactory : EntryRegistry.creatorFactories){
				if(alreadyTriedCreatorFactories.contains(creatorFactory.getCodeName()))
					throw new InvalidConfigurationValueException("CreatorFactory codename: " + creatorFactory.getCodeName() + " already used before " + creatorFactory.getClass().getName());
				
				alreadyTriedCreatorFactories.add(creatorFactory.getCodeName());
				for(IConfigurationRetriever configurationRetriever : configurationManager.getExperimentsConfiguration(creatorFactory.getCodeName())){
					final String experimentName     = configurationRetriever.getProperty("experiment.name");
					final String experimentCategory = configurationRetriever.getProperty("experiment.category");
					
					final String compoundName = experimentName + "@" + experimentCategory;
					if(alreadyRegisteredExperiments.contains(compoundName))
						throw new InvalidConfigurationValueException("Experiment " + compoundName + " already registered");
					alreadyRegisteredExperiments.add(compoundName);
					
					final ExperimentEntry entry = new ExperimentEntry(experimentCategory, experimentName, creatorFactory.createExperimentCreator(configurationRetriever), configurationRetriever);
					
					EntryRegistry.entries.add(entry);
				}
			}
		}catch(ExperimentCreatorInstanciationException exc){
			throw new InvalidConfigurationValueException("Misconfigured experiment: " + exc.getMessage(), exc);
		}
	}
	
	public static IConfigurationRetriever getExperimentConfigurationRetriever(ExperimentID experimentId){
		//System.out.println("DBG: Now listing entries");
		for(ExperimentEntry entry : EntryRegistry.entries) {
			//System.out.println("DBG: " + entry.getExperimentID());
			if(entry.getExperimentID().equals(experimentId))
				return entry.getConfigurationRetriever();
		}

		throw new IllegalArgumentException("Experiment ID is missing from the configuration file or the registry! " + experimentId);
	} 
}
