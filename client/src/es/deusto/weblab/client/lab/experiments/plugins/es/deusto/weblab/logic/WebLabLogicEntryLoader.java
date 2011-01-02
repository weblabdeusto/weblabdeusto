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

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.IExperimentEntryLoader;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class WebLabLogicEntryLoader implements IExperimentEntryLoader {

	@Override
	public String getCodeName() {
		return "logic";
	}

	@Override
	public ExperimentCreator loadExperimentEntry(final IConfigurationRetriever configurationRetriever) {
		return new ExperimentCreator(MobileSupport.full, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new WebLabLogicExperiment(configurationRetriever, boardController));
					}
					
					@Override
					public void onFailure(Throwable e){
						callback.onFailure(e);
					}
				});
			}
			
			@Override
			public void createMobile(final IBoardBaseController boardController, final IExperimentLoadedCallback callback){
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new MobileWebLabLogicExperiment(configurationRetriever, boardController));
					}
					
					@Override
					public void onFailure(Throwable e){
						callback.onFailure(e);
					}
				});
			}
		};
	}

}
