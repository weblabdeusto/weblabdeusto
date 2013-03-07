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

import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IDisposableWidgetsContainer;
import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;
import es.deusto.weblab.client.ui.widgets.WlTimer;

public class MainPanel extends Composite implements IDisposableWidgetsContainer, IStatusUpdatable, IPictureManager  {

	@UiField(provided=true) WebcamPanel webcamPanel;
	@UiField(provided=true) WlTimer timer;
	
	@UiField BallPanel redBall;
	@UiField BallPanel blueBall;
	@UiField BallPanel yellowBall;
	@UiField BallPanel whiteBall;
	
	@UiField Label webcamLabel;
	@UiField Label pictureLabel;
	
	@UiField Image picture;
	
	private static MainPanelUiBinder uiBinder = GWT.create(MainPanelUiBinder.class);

	interface MainPanelUiBinder extends UiBinder<Widget, MainPanel> { }

	public MainPanel(IBoardBaseController boardController, IConfigurationRetriever configurationRetriever, int time, String initialConfiguration, Status initialStatus) {
		this.timer = new WlTimer(false);
		this.webcamPanel = new WebcamPanel(configurationRetriever, initialConfiguration);
		
		initWidget(uiBinder.createAndBindUi(this));
		
		this.whiteBall.setBoardController(boardController);
		this.blueBall.setBoardController(boardController);
		this.redBall.setBoardController(boardController);
		this.yellowBall.setBoardController(boardController);
		
		this.whiteBall.setGlobalUpdater(this);
		this.blueBall.setGlobalUpdater(this);
		this.redBall.setGlobalUpdater(this);
		this.yellowBall.setGlobalUpdater(this);

		this.whiteBall.setPictureManager(this);
		this.blueBall.setPictureManager(this);
		this.redBall.setPictureManager(this);
		this.yellowBall.setPictureManager(this);

		
		this.timer.updateTime(time);
		this.timer.start();
		
		this.webcamPanel.start();
		
		updateStatus(initialStatus);
	}


	@Override
	public IWlDisposableWidget [] getDisposableWidgets() {
		final List<IWlDisposableWidget> disposables = new Vector<IWlDisposableWidget>();
		
		for(IWlDisposableWidget disposable : this.webcamPanel.getDisposableWidgets())
			disposables.add(disposable);
		
		disposables.add(this.timer);
		return disposables.toArray(new IWlDisposableWidget[]{});
	}

	@Override
	public Widget asGwtWidget() {
		return this;
	}


	@Override
	public void updateStatus(Status status) {
		this.whiteBall.updateStatus(status);
		this.blueBall.updateStatus(status);
		this.redBall.updateStatus(status);
		this.yellowBall.updateStatus(status);
	}


	@Override
	public void takePicture() {
		this.picture.setVisible(true);
		this.picture.setUrl(this.webcamPanel.webcam.getUrl());
		
		this.pictureLabel.setVisible(true);
		this.webcamLabel.setVisible(true);
	}
}
