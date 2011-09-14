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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

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

}
