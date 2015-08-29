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
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.uibinder.client.UiHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;

public class BallPanel extends Composite implements IStatusUpdatable {
	
	private static Resources res = GWT.create(Resources.class);

	private static BallWidgetUiBinder uiBinder = GWT.create(BallWidgetUiBinder.class);

	interface BallWidgetUiBinder extends UiBinder<Widget, BallPanel> {
	}
	
	@UiField Label ballName;
	@UiField Image ballImg;
	@UiField Image upButton;
	@UiField Image downButton;
	@UiField Button takePictureButton;
	
	private Color color = Color.blue;
	private boolean status = false;
	private IBoardBaseController controller = null;
	private IStatusUpdatable globalUpdatable = null;
	private IPictureManager pictureManager = null;
	
	private final IResponseCommandCallback callback = new IResponseCommandCallback(){
		
		@Override
		public void onFailure(CommException e) {
			Window.alert("Error: " + e.getMessage() + "; please do contact administrator.");
			e.printStackTrace();
		}

		@Override
		public void onSuccess(ResponseCommand responseCommand) {
			if(BallPanel.this.globalUpdatable != null) {
				BallPanel.this.globalUpdatable.updateStatus(new Status(responseCommand.getCommandString()));
			}
		}
	};

	public BallPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		
		switchButton(true);
	}
	
	public BallPanel(Color color) {
		this();
		setColor(color);
	}
	
	private void sendButtonCommand(String on) {
		if(this.controller != null) {
			disableButtons();
			this.controller.sendCommand("ball:" + this.color.name() + ":" + on, this.callback);
		}
	}
	
	@UiHandler("upButton")
	public void onUpButtonClickHandler(@SuppressWarnings("unused") ClickEvent event) {
		System.out.println("Ball " + this.color + ": up pressed; with status " + this.status + " and controller being null: " + (this.controller == null));
		if(!this.status) // If it's down
			sendButtonCommand("true");
	}

	@UiHandler("downButton")
	public void onDownButtonClickHandler(@SuppressWarnings("unused") ClickEvent event) {
		System.out.println("Ball " + this.color + ": down pressed; with status " + this.status + " and controller being null: " + (this.controller == null));
		if(this.status) // If it's up
			sendButtonCommand("false");
	}
	
	@UiHandler("takePictureButton")
	public void onTakePictureClickHandler(@SuppressWarnings("unused") ClickEvent event) {
		if(this.pictureManager != null) {
			this.pictureManager.takePicture();
		}
	}
	
	void setBoardController(IBoardBaseController controller) {
		this.controller = controller;
	}
	
	void setGlobalUpdater(IStatusUpdatable updater) {
		this.globalUpdatable = updater;
	}
	
	void setPictureManager(IPictureManager pictureManager) {
		if(pictureManager != null) {
			this.pictureManager = pictureManager;
			this.takePictureButton.setVisible(true);
		} else {
			this.takePictureButton.setVisible(false);
		}
	}
	
	public void setColor(Color color) {
		this.color = color;
		
		switch(this.color) {
			
			case blue: 
				this.ballImg.setResource(res.blue());
				break;
				
			case red: this.ballImg.setResource(res.red());
				break;
				
			case white: this.ballImg.setResource(res.white());
				break;
			
			case yellow: this.ballImg.setResource(res.yellow());
				break;
			
		}
		
		this.ballName.setText(this.color.name());
	}

	private void switchButton(boolean newState) {
		this.status = newState;
		if(newState) {
			this.upButton.setStyleName("wl-disabled-img-button");
			this.downButton.setStyleName("wl-img-button");
		} else {
			this.downButton.setStyleName("wl-disabled-img-button");
			this.upButton.setStyleName("wl-img-button");
		}
	}
	
	private void disableButtons() {
		this.downButton.setStyleName("wl-disabled-img-button");
		this.upButton.setStyleName("wl-disabled-img-button");
	}
	
	@Override
	public void updateStatus(Status status) {
		Boolean b = status.getColor(this.color);
		if(b != null) {
			switchButton(b.booleanValue());
		}
	}
}
