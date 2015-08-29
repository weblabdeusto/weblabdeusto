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

package es.deusto.weblab.client.lab.experiments.util.applets.java;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationException;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.IHasExperimentParameters;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentCreatorInstanciationException;
import es.deusto.weblab.client.lab.experiments.util.applets.AbstractCreatorFactory;

public class JavaAppletCreatorFactory implements IExperimentCreatorFactory, IHasExperimentParameters {

	public static final ExperimentParameter JAR_FILE = new ExperimentParameter("jar.file", ExperimentParameter.Type.string, "The jar file URL");
	public static final ExperimentParameter CODE = new ExperimentParameter("code", ExperimentParameter.Type.string, "The applet class");
	
	@Override
	public String getCodeName() {
		return "java";
	}

	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) throws ExperimentCreatorInstanciationException{
		final int width;
		final int height;
		final String archive;
		final String code;
		final String message;		
		
		try{
			width   = configurationRetriever.getIntProperty(AbstractCreatorFactory.WIDTH);
			height  = configurationRetriever.getIntProperty(AbstractCreatorFactory.HEIGHT);
			archive = configurationRetriever.getProperty(JAR_FILE);
			code    = configurationRetriever.getProperty(CODE);
			message = configurationRetriever.getProperty(AbstractCreatorFactory.MESSAGE);
		}catch(ConfigurationException exc){
			throw new ExperimentCreatorInstanciationException("Misconfigured experiment " + getCodeName() + ": " + exc.getMessage(), exc);
		}
		
		return new ExperimentCreator(MobileSupport.disabled, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new JavaAppletsExperiment(
								configurationRetriever,
								boardController,
								archive, code,
								width, height, message
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
											JAR_FILE, CODE };
	}

}
