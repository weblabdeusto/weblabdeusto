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

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentInstanciationException;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentNotFoundException;
import es.deusto.weblab.client.lab.experiments.util.applets.flash.FlashAppExperimentBase;
import es.deusto.weblab.client.lab.experiments.util.applets.java.JavaAppletExperimentBase;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

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
	
	// 
	// TODO: not called yet!!! When called, remove the flash / java / etc. experiments from the "entries" list
	// Should be called when the ConfigurationManager has been loaded
	// 
	public static void loadExperiments(IConfigurationManager configurationManager) throws InvalidConfigurationValueException, ConfigurationKeyNotFoundException{
		for(IConfigurationRetriever flashExperimentConfiguration : configurationManager.getExperimentsConfiguration("flash")){
			
			final String experimentName     = flashExperimentConfiguration.getProperty("experiment.name");
			final String experimentCategory = flashExperimentConfiguration.getProperty("experiment.category");
			final int width                 = flashExperimentConfiguration.getIntProperty("width");
			final int height                = flashExperimentConfiguration.getIntProperty("height");
			final String swfFile            = flashExperimentConfiguration.getProperty("swf.file");
			final String message            = flashExperimentConfiguration.getProperty("message");
			
			final ExperimentEntry entry = new ExperimentEntry(experimentCategory, experimentName, MobileSupport.disabled){
				@Override
				public void createWeb( final IConfigurationRetriever configurationRetriever, final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
					GWT.runAsync(new RunAsyncCallback() {
						@Override
						public void onSuccess() {
							callback.onExperimentLoaded(new FlashAppExperimentBase(configurationRetriever, boardController, width, height, swfFile, "", message));
						}
						
						@Override
						public void onFailure(Throwable e){
							callback.onFailure(e);
						}
					});
				}
			};
			
			EntryRegistry.entries.add(entry);
		}
		
		for(IConfigurationRetriever javaExperimentConfiguration : configurationManager.getExperimentsConfiguration("java")){
			
			final String experimentName     = javaExperimentConfiguration.getProperty("experiment.name");
			final String experimentCategory = javaExperimentConfiguration.getProperty("experiment.category");
			final int width                 = javaExperimentConfiguration.getIntProperty("width");
			final int height                = javaExperimentConfiguration.getIntProperty("height");
			final String archive            = javaExperimentConfiguration.getProperty("jar.file");
			final String code               = javaExperimentConfiguration.getProperty("code");
			final String message            = javaExperimentConfiguration.getProperty("message");
			
			final ExperimentEntry entry = new ExperimentEntry(experimentCategory, experimentName, MobileSupport.disabled){
				@Override
				public void createWeb( final IConfigurationRetriever configurationRetriever, final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
					GWT.runAsync(new RunAsyncCallback() {
						@Override
						public void onSuccess() {
							callback.onExperimentLoaded(new JavaAppletExperimentBase(configurationRetriever, boardController, width, height, archive, code, message));
						}
						
						@Override
						public void onFailure(Throwable e){
							callback.onFailure(e);
						}
					});
				}
			};
			EntryRegistry.entries.add(entry);
		}
		configurationManager.getExperimentsConfiguration("vm");
	}
}
