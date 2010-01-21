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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class WlTimer implements IWlWidget{

	public static int DEFAULT_START_VALUE = 5;
	
	public interface IWlTimerFinishedCallback{
		public void onFinished();
	}
	
	private final Label label;
	private int time;
	private Timer timer;
	private IWlTimerFinishedCallback timerFinishedCallback = null;
	
	public WlTimer(){
		this(WlTimer.DEFAULT_START_VALUE);
	}
	
	public WlTimer(int startValue){
		this.time = startValue;
		this.label = new Label(Integer.toString(startValue));
		this.timer = new Timer(){
			@Override
			public void run(){
				WlTimer.this.decrement();
				if(WlTimer.this.time == 0){
					WlTimer.this.timer.cancel();
					if(WlTimer.this.timerFinishedCallback != null)
						WlTimer.this.timerFinishedCallback.onFinished();
				}
			}
		};
		this.timer.scheduleRepeating(1000);
	}
	
	public void setTimerFinishedCallback(IWlTimerFinishedCallback callback){
		this.timerFinishedCallback = callback;
	}
	
	protected void decrement(){
		if(this.time > 0){
			--this.time;
			this.label.setText(Integer.toString(this.time));
		}
	}
	
	public int getTime(){
		return this.time;
	}
	
	public void updateTime(int time){
		this.time = time;
		this.label.setText(Integer.toString(time));
	}

	public void dispose(){
		if(this.timer != null){
			this.timer.cancel();
			this.timer = null;
		}
	}
	
	public void setStyleName(String style){
		this.label.setStyleName(style);
	}
	
	@Override
	public Widget getWidget() {
		return this.label;
	}

}
