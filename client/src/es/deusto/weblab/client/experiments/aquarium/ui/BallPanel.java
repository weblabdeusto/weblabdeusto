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
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class BallPanel extends Composite implements IStatusUpdatable {
	
	private static Resources res = GWT.create(Resources.class);

	private static BallWidgetUiBinder uiBinder = GWT.create(BallWidgetUiBinder.class);

	interface BallWidgetUiBinder extends UiBinder<Widget, BallPanel> {
	}
	
	@UiField Label ballName;
	@UiField Image ballImg;
	
	private Color color = Color.blue;

	public BallPanel() {
		initWidget(uiBinder.createAndBindUi(this));
		
		// img.setStyleName("wl-disabled-img-button");
		// img.setStyleName("wl-img-button");
	}
	
	public BallPanel(Color color) {
		this();
		setColor(color);
	}

	public void setColor(Color color) {
		this.color = color;
		
		switch(this.color) {
			
			case blue: 
				this.ballImg.setResource(res.blue());
				break;
				
			case red: this.ballImg.setResource(res.red());
				break;
				
			case green: this.ballImg.setResource(res.green());
				break;
			
			case yellow: this.ballImg.setResource(res.yellow());
				break;
			
		}
		
		this.ballName.setText(this.color.name());
	}

	@Override
	public void updateStatus(Status status) {
		// TODO Auto-generated method stub
		
	}
}
