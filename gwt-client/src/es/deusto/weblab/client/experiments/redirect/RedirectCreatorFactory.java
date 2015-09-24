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

package es.deusto.weblab.client.experiments.redirect;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;
import com.google.gwt.user.client.Window;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.experiments.redirect.RedirectExperiment.LinkPresentation;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.ExperimentParameterDefault;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.IHasExperimentParameters;

public class RedirectCreatorFactory implements IExperimentCreatorFactory, IHasExperimentParameters {

	private final static String DEFAULT_WIDTH;
	private final static String DEFAULT_HEIGHT;
	static {
		int height, width;
		if (GWT.isClient()) {
			height = Window.getClientHeight();
			width  = Window.getClientWidth();
		} else {
			height = 800;
			width  = 1000;
		}
		DEFAULT_HEIGHT = "" + height;
		DEFAULT_WIDTH  = "" + width;
	}
	
	public static final ExperimentParameterDefault LINK_PRESENTATION = new ExperimentParameterDefault("link.presentation", "Link presentation (redirection, iframe, popup)", LinkPresentation.redirection.name());
	public static final ExperimentParameterDefault EXTERNAL_WIDTH = new ExperimentParameterDefault("external.width", "If popup or iframe,  width", DEFAULT_WIDTH);
	public static final ExperimentParameterDefault EXTERNAL_HEIGHT = new ExperimentParameterDefault("external.height", "If popup or iframe,  height", DEFAULT_HEIGHT);
	
	@Override
	public String getCodeName() {
		return "redirect";
	}

	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) {
		return new ExperimentCreator(MobileSupport.full, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new RedirectExperiment(
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
		return new ExperimentParameter[] { LINK_PRESENTATION, EXTERNAL_HEIGHT, EXTERNAL_WIDTH };
	}
}
