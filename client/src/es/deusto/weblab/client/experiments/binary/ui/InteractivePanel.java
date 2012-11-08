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
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlSwitch.SwitchEvent;

class InteractivePanel extends Composite {

	interface InteractivePanelUiBinder extends UiBinder<Widget, InteractivePanel> { }
	private static InteractivePanelUiBinder uiBinder = GWT.create(InteractivePanelUiBinder.class);

	@UiField WlSwitch switch1;
	@UiField WlSwitch switch2;
	@UiField WlSwitch switch3;
	@UiField WlSwitch switch4;
	@UiField Label exerciseLabel;

	private final IBoardBaseController controller;
	private final MainPanel mainPanel;
	
	public InteractivePanel(MainPanel mainPanel, IBoardBaseController controller, String label) {
		this.controller = controller;
		this.mainPanel  = mainPanel;
		initWidget(uiBinder.createAndBindUi(this));
		this.exerciseLabel.setText(label);
	}
	
	@SuppressWarnings("unused")
	@UiHandler("otherCodeButton")
	public void onOtherCodeButton(ClickEvent event) {
		this.mainPanel.loadButtons();
	}

	@UiHandler("switch1")
	public void onSwitch1click(SwitchEvent event) {
		processSwitch(1, event.isOn());
	}
	
	@UiHandler("switch2")
	public void onSwitch2click(SwitchEvent event) {
		processSwitch(2, event.isOn());
	}
	
	@UiHandler("switch3")
	public void onSwitch3click(SwitchEvent event) {
		processSwitch(3, event.isOn());
	}
	
	@UiHandler("switch4")
	public void onSwitch4click(SwitchEvent event) {
		processSwitch(4, event.isOn());
	}
	
	private void processSwitch(int number, boolean state) {
		final String message = "switch:" + number + "," + (state?"on":"off");
		if(this.controller != null) {
			this.controller.sendCommand(message);
		} else{
			System.err.println("There is no controller set; skipping message: " + message);
		}
	}
}
