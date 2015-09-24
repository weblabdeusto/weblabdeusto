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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;


// TODO: I've made WlWaitingLabel extend Label so that it can be used with
// UIBinder. Consider alternatives. (I've tried overloading
// WlVerticalPanel's Add(), but it is ambiguous, because quite a few
// types (such as WlVerticalPanel itself) seem to be both a 
// Widget and a IWlWidget.

public class WlWaitingLabel extends Label implements IWlWidget{

	private static final int MOVING_TIME = 500;
	private static final int MAX_DOTS    = 3;
	
	//private final Label label = this;
	private String realText;
	private boolean running;
	private int counter;
	private Timer currentTimer = null;
	
	public WlWaitingLabel(){
		this.running = false;
		//this.label = new Label();
		this.counter = 0;
	}
	
	public WlWaitingLabel(String text){
		this();
		this.setText(text);
	}
	
	@Override
	public void setText(String text){
		this.realText = text;
		this.counter = 0;
		this.showText(text);
	}
	
	private void showText(String text){
		super.setText(text);
	}
	
	@Override
	public String getText(){
		return this.realText;
	}
	
	public void start(){
		this.running = true;
		this.queueProcessingDots();
	}
	
	private void processDots(){
		WlWaitingLabel.this.counter++;
		if(WlWaitingLabel.this.counter > WlWaitingLabel.MAX_DOTS)
			WlWaitingLabel.this.counter = 0;
		
		String dots = "";
		for(int i = 0; i < WlWaitingLabel.this.counter; ++i)
			dots += ".";
		
		final String visibleText = this.realText + dots;
		this.showText(visibleText);
		
		this.queueProcessingDots();
	}

	private void queueProcessingDots(){
		this.currentTimer = new Timer(){
			@Override
			public void run(){
				if(WlWaitingLabel.this.running)
					WlWaitingLabel.this.processDots();
			}
		};
		this.currentTimer.schedule(WlWaitingLabel.MOVING_TIME);
	}
	
	public void stop(){
		if(this.running){
			if(this.currentTimer != null)
				this.currentTimer.cancel();
			
			this.currentTimer = null;
			this.running = false;
		}
	}
	
	@Override
	public Widget getWidget() {
		return this;
	}

	@Override
	public void dispose() {
		this.stop();
	}
}
