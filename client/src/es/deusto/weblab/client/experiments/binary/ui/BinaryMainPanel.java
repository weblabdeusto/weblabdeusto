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
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.ui.widgets.WlSwitch;
import es.deusto.weblab.client.ui.widgets.WlSwitch.SwitchEvent;
import es.deusto.weblab.client.ui.widgets.WlTimer;
import es.deusto.weblab.client.ui.widgets.WlWebcam;

public class BinaryMainPanel extends Composite {
	
	private static BinaryMainPanelUiBinder uiBinder = GWT.create(BinaryMainPanelUiBinder.class);
	
	@UiField WlWebcam camera;
	@UiField WlTimer timer;
	
	@UiField WlSwitch switch1;
	@UiField WlSwitch switch2;
	@UiField WlSwitch switch3;
	@UiField WlSwitch switch4;
	
	private IBoardBaseController controller;
	
	interface BinaryMainPanelUiBinder extends UiBinder<Widget, BinaryMainPanel> {
	}
	
	public BinaryMainPanel() {
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public BinaryMainPanel(IBoardBaseController controller) {
		this.controller = controller;
		initWidget(uiBinder.createAndBindUi(this));
	}
	
	public WlWebcam getWebcam() {
		return this.camera;
	}
	
	public WlTimer getTimer() {
		return this.timer;
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
		final String message = "TURN SWITCH " + number + " " + (state?"ON":"OFF");
		if(this.controller != null) {
			this.controller.sendCommand(message);
		} else{
			System.err.println("There is no controller set; skipping message: " + message);
		}
	}
}
