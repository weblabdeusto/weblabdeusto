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
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class BallPanel extends Composite {

	private static BallWidgetUiBinder uiBinder = GWT
			.create(BallWidgetUiBinder.class);

	interface BallWidgetUiBinder extends UiBinder<Widget, BallPanel> {
	}

	public BallPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		
		// img.setStyleName("wl-disabled-img-button");
	}

}
