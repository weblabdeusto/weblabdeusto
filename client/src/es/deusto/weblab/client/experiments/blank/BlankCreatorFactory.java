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
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.experiments.blank;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.experiments.blank.ui.BlankExperiment;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentCreatorInstanciationException;

public class BlankCreatorFactory  implements IExperimentCreatorFactory {

	private final MobileSupport mobileSupport;
	
	public BlankCreatorFactory(MobileSupport mobileSupport){
		this.mobileSupport = mobileSupport;
	}
	
	public BlankCreatorFactory() {
		this.mobileSupport = MobileSupport.full;
	}
	
	@Override
	public String getCodeName() {
		return "blank";
	}
	
	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) throws ExperimentCreatorInstanciationException {
		return new ExperimentCreator(this.mobileSupport, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new BlankExperiment(
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
