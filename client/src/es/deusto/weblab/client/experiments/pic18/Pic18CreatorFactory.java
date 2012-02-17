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
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.pic18;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.experiments.pic18.ui.Pic18Experiment;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;

public class Pic18CreatorFactory implements IExperimentCreatorFactory {

	@Override
	public String getCodeName() {
		return "pic18";
	}

	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) {
		return new ExperimentCreator(MobileSupport.limited, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new Pic18Experiment(
								configurationRetriever,
								boardController
							));
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
