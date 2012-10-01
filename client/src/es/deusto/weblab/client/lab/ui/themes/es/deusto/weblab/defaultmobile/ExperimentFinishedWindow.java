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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultmobile;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.History;
import com.google.gwt.user.client.Window.Location;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.HistoryProperties;

public class ExperimentFinishedWindow extends Composite {

	private static ExperimentFinishedWindowUiBinder uiBinder = GWT
			.create(ExperimentFinishedWindowUiBinder.class);

	interface ExperimentFinishedWindowUiBinder
			extends
				UiBinder<Widget, ExperimentFinishedWindow> {
	}

	public ExperimentFinishedWindow() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	@UiHandler("backButton")
	public void back(@SuppressWarnings("unused") ClickEvent event) {
		final String backURL = HistoryProperties.getValue(HistoryProperties.BACK);
		if(backURL == null)
			History.back();
		else {
			final String decoded = HistoryProperties.decode(backURL);
			Location.assign(decoded);
		}
	}
}
