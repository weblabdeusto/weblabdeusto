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

package es.deusto.weblab.client.experiments.binary.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.RadioButton;
import com.google.gwt.user.client.ui.Widget;

class InitializationPanel extends Composite {

	private static InitializationPanelUiBinder uiBinder = GWT.create(InitializationPanelUiBinder.class);
	
	@UiField RadioButton optionBCD;
	@UiField RadioButton optionOther;

	interface InitializationPanelUiBinder extends UiBinder<Widget, InitializationPanel> { }

	public InitializationPanel() {
		initWidget(uiBinder.createAndBindUi(this));
	}

	public String getInitialExcercise() {
		if(this.optionBCD.getValue())
			return "bcd";
		return "other";
	}

}
