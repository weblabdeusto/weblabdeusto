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

package es.deusto.weblab.client.experiments.labview;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.experiments.labview.ui.LabViewExperiment;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.ExperimentParameterDefault;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.IHasExperimentParameters;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;

public class LabVIEWCreatorFactory implements IExperimentCreatorFactory, IHasExperimentParameters {
	
	public static final ExperimentParameterDefault SEND_FILE = new ExperimentParameterDefault("send.file", "Send file or not", false);
	
	@Override
	public String getCodeName() {
		return "labview";
	}
	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) {
		return	new ExperimentCreator(MobileSupport.disabled, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new LabViewExperiment(
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
	@Override
	public ExperimentParameter[] getParameters() {
		return new ExperimentParameter [] { SEND_FILE };
	}
}
