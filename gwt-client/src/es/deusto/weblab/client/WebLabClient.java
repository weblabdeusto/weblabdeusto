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
package es.deusto.weblab.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.shared.GWT;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.EntryRegistry;
import es.deusto.weblab.client.lab.experiments.ExperimentBase;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.JSBoardBaseController;
import es.deusto.weblab.client.lab.experiments.exceptions.ExperimentCreatorInstanciationException;

public class WebLabClient implements EntryPoint {
    
	public static String baseLocation;
	private static final String MAIN_SLOT = "weblab_slot";
	
    public void putWidget(Widget widget){
        while(RootPanel.get(WebLabClient.MAIN_SLOT).getWidgetCount() > 0)
            RootPanel.get(WebLabClient.MAIN_SLOT).remove(0);
        RootPanel.get(WebLabClient.MAIN_SLOT).add(widget);
    }
    
    public void showError(String message) {
    	putWidget(new Label(message));
    }

	@Override
	public void onModuleLoad() {
		final IBoardBaseController boardBaseController = new JSBoardBaseController();
		WebLabClient.baseLocation = JSBoardBaseController.getBaseLocation();
		final IConfigurationRetriever configurationRetriever = JSBoardBaseController.getExperimentConfiguration();
		
		final String clientCodeName = JSBoardBaseController.getClientCodeName();
		final IExperimentCreatorFactory experimentCreatorFactory = getExperimentFactory(clientCodeName);
		if (experimentCreatorFactory == null) {
			showError("client code name " + clientCodeName + " not implemented in GWT");
			return;
		}
		
		final ExperimentCreator creator;
		try {
			creator = experimentCreatorFactory.createExperimentCreator(configurationRetriever);
		} catch (ExperimentCreatorInstanciationException e1) {
			showError("Could not instantiate experiment: " + e1.getMessage());
			e1.printStackTrace();
			return;
		}

		final IExperimentLoadedCallback callback = new IExperimentLoadedCallback() {
			
			@Override
			public void onFailure(Throwable e) {
				GWT.log("Client code name " + clientCodeName + " not working", e);
				showError("client code name " + clientCodeName + " not implemented in GWT");
			}
			
			@Override
			public void onExperimentLoaded(ExperimentBase experiment) {
				WebLabClient.this.putWidget(experiment.getWidget());
				JSBoardBaseController.registerExperiment(experiment);
			}
		};

		if (JSBoardBaseController.isMobile()) {
			creator.createMobile(boardBaseController, callback);
		} else {
			creator.createWeb(boardBaseController, callback);
		}
	}

	private IExperimentCreatorFactory getExperimentFactory(final String clientCodeName) {
		IExperimentCreatorFactory currentCreatorFactory = null;
		for(IExperimentCreatorFactory creatorFactory : EntryRegistry.creatorFactories) {
			if (creatorFactory.getCodeName().equals(clientCodeName)) {
				currentCreatorFactory = creatorFactory;
			}
		}
		return currentCreatorFactory;
	}
}
