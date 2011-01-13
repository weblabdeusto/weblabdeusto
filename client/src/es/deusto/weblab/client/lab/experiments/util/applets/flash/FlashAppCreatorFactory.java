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

package es.deusto.weblab.client.lab.experiments.util.applets.flash;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.WlConfigurationException;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentCreatorInstanciationException;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class FlashAppCreatorFactory implements IExperimentCreatorFactory {

	@Override
	public String getCodeName() {
		return "flash";
	}

	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) throws ExperimentCreatorInstanciationException {
		final int width;
		final int height;
		final String swfFile;
		final String message;
		
		try{
			width   = configurationRetriever.getIntProperty("width");
			height  = configurationRetriever.getIntProperty("height");
			swfFile = configurationRetriever.getProperty("swf.file");
			message = configurationRetriever.getProperty("message");
		}catch(WlConfigurationException icve){
			throw new ExperimentCreatorInstanciationException("Misconfigured experiment: " + getCodeName() + ": " + icve.getMessage(), icve);
		}

		return new ExperimentCreator(MobileSupport.disabled, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
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
	}

}
