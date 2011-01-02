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

package es.deusto.weblab.client.lab.experiments.util.applets.java;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.IExperimentEntryLoader;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.ui.BoardBase.IBoardBaseController;

public class JavaAppletEntryLoader implements IExperimentEntryLoader{

	@Override
	public String getCodeName() {
		return "java";
	}

	@Override
	public ExperimentCreator loadExperimentEntry(final IConfigurationRetriever configurationRetriever) {
		return new ExperimentCreator(MobileSupport.disabled, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				/* TODO
				final int width                 = javaExperimentConfiguration.getIntProperty("width");
				final int height                = javaExperimentConfiguration.getIntProperty("height");
				final String archive            = javaExperimentConfiguration.getProperty("jar.file");
				final String code               = javaExperimentConfiguration.getProperty("code");
				final String message            = javaExperimentConfiguration.getProperty("message");
				*/
				
				final int width      = 500;
				final int height     = 350;
				final String archive = "WeblabJavaSample.jar";
				final String code    = "es.deusto.weblab.client.experiment.plugins.es.deusto.weblab.javadummy.JavaDummyApplet";
				final String message = "Note: This is not a real experiment, it's just a demo so as to show that WebLab-Deusto can integrate different web technologies (such as Java Applets in this experiment). This demostrates that developing experiments in WebLab-Deusto is really flexible."; 
				
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
	}
}
