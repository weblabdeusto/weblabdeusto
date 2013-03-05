/*
* Copyright (C) 2012 onwards University of Deusto
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

package es.deusto.weblab.client.experiments.aquarium.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class WebcamPanel extends Composite {

	private static WebcamPanelUiBinder uiBinder = GWT.create(WebcamPanelUiBinder.class);

	@UiField(provided=true) WlWebcam webcam;
	
	interface WebcamPanelUiBinder extends UiBinder<Widget, WebcamPanel> {
	}

	public WebcamPanel(IConfigurationRetriever configurationRetriever) {
		
		this.webcam = new WlWebcam();
		initWidget(uiBinder.createAndBindUi(this));
	}

}
