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

package es.deusto.weblab.client.lab.experiments.util.applets.flash;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationException;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.ExperimentParameterDefault;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.IHasExperimentParameters;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentCreatorInstanciationException;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractCreatorFactory;

public class FlashAppCreatorFactory implements IExperimentCreatorFactory, IHasExperimentParameters {

	public static final ExperimentParameterDefault FLASH_TIMEOUT = new ExperimentParameterDefault("flash.timeout", "Time given for Flash to load", 40);
	public static final ExperimentParameter SWF_FILE = new ExperimentParameter("swf.file", ExperimentParameter.Type.string, "SWF file");
	
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
			width   = configurationRetriever.getIntProperty(AbstractCreatorFactory.WIDTH);
			height  = configurationRetriever.getIntProperty(AbstractCreatorFactory.HEIGHT);
			swfFile = configurationRetriever.getProperty(SWF_FILE);
			message = configurationRetriever.getProperty(AbstractCreatorFactory.MESSAGE);
		}catch(ConfigurationException icve){
			throw new ExperimentCreatorInstanciationException("Misconfigured experiment: " + getCodeName() + ": " + icve.getMessage(), icve);
		}

		return new ExperimentCreator(MobileSupport.disabled, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new FlashExperiment(
								configurationRetriever,
								boardController, swfFile,
								width, height, "", message
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
		return new ExperimentParameter [] { AbstractCreatorFactory.WIDTH, AbstractCreatorFactory.HEIGHT, AbstractCreatorFactory.MESSAGE, AbstractCreatorFactory.PAGE_FOOTER,
											SWF_FILE, FLASH_TIMEOUT};
	}
}
