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
* Author: FILLME
*
*/

package es.deusto.weblab.client.experiments.robot_maze.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

public class InitialPanel extends Composite {

	private static InitialPanelUiBinder uiBinder = GWT
			.create(InitialPanelUiBinder.class);

	interface InitialPanelUiBinder extends UiBinder<Widget, InitialPanel> {
	}

	public InitialPanel() {
		initWidget(uiBinder.createAndBindUi(this));
	}
}
