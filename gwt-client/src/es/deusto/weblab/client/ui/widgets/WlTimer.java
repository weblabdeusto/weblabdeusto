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
* 		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AudioElement;
import com.google.gwt.media.client.Audio;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.audio.AudioManager;

public class WlTimer extends Label implements IWlWidget{

	public static final int DEFAULT_START_VALUE = 5;
	public static final String DEFAULT_STYLE = "wl-time_remaining"; 
	
	public interface IWlTimerFinishedCallback{
		public void onFinished();
	}
	
	private int time;
	private Timer timer;
	private IWlTimerFinishedCallback timerFinishedCallback = null;
	
	private int timeRunningOutAudioLimit = 6;

	public void start() {
		this.setText(Integer.toString(this.time));
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
	
	/**
	 * Creates a WlTimer using the default start value.
	 * @param startNow If true, the timer is automatically started.
	 * If false, the timer is not started until the method start is called.
	 */
	public WlTimer(boolean startNow) {
		this.time = WlTimer.DEFAULT_START_VALUE;
		setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		setStyleName(DEFAULT_STYLE);
		if(startNow)
			this.start();
	}
	
	/**
	 * Creates a WlTimer using the specified start value.
	 * @param startValue The value to initialise the timer.
	 * @param startNow If true, the timer is automatically started.
	 * If false, the timer is not started until the method start is called.
	 */
	public WlTimer(int startValue, boolean startNow) {
		this.time = startValue;
		this.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		setStyleName(DEFAULT_STYLE);
		if(startNow)
			this.start();
	}
	
	public WlTimer(){
		this(WlTimer.DEFAULT_START_VALUE);
	}
	
	public WlTimer(int startValue){
		this.time = startValue;
		setStyleName(DEFAULT_STYLE);
		this.start();
	}
	
	/**
	 * Sets the point of time from which the time running out audio will start playing.
	 * @param limit Limit, in seconds, from which the audio will start playing.
	 */
	public void setTimeRunningOutAudioLimit(int limit) {
		this.timeRunningOutAudioLimit = limit;
	}
	
	public void setTimerFinishedCallback(IWlTimerFinishedCallback callback){
		this.timerFinishedCallback = callback;
	}
	
	/**
	 * Updates the label which describes the time left. The time left is internally measured
	 * in seconds, but this method will display it in the hh:mm:ss, mm:ss or just ss format,
	 * depending on the amount of seconds left.
	 */
	private void updateTimeString() {
		int seconds = this.time % 60;
		int minutes = (this.time / 60) % 60;
		int hours = this.time / 3600;
		
		final StringBuilder sb = new StringBuilder();
		
		if(hours > 0) {
			if(hours < 10)
				sb.append('0');
			sb.append(hours);
			sb.append(':');
		}
		
		if(minutes > 0) {
			if(minutes < 10)
				sb.append('0');
			sb.append(minutes);
			sb.append(':');
		}
		
		if(seconds < 10)
			sb.append('0');
		sb.append(seconds);
		
		this.setText(sb.toString());
	}
	
	protected void decrement(){
		if(this.time > 0){
			--this.time;
			this.updateTimeString();
		}
		
		if(AudioManager.getInstance().getSoundEnabled()) {
			Audio timeRunningOutAudio = Audio.createIfSupported();
			if(this.time == this.timeRunningOutAudioLimit && AudioManager.getInstance() != null) {
				System.out.println(this.getParent());
				final AudioElement effect = timeRunningOutAudio.getAudioElement();
				effect.setSrc(GWT.getModuleBaseURL() + "snd/clock.wav");
				effect.setLoop(true);
				effect.play();
			} else if( this.time == 0 ) {
				final AudioElement effect = timeRunningOutAudio.getAudioElement();
				effect.setLoop(false);
				effect.pause();
	
				// TODO: Make sure that this isn't a memory leak. There does not seem to be any method that provides a 
				// "destroy" rather than "pause". Make also sure that there is no case under which a timer can not reach zero.
				// Otherwise, the sound might play forever, which is significantly annoying.
			}
		}
		
	}
	
	public int getTime(){
		return this.time;
	}
	
	public void updateTime(int time){
		this.time = time;
		this.updateTimeString();
	}

	@Override
	public void dispose(){
		if(this.timer != null){
			this.timer.cancel();
			this.timer = null;
		}
	}
	
	@Override
	public Widget getWidget() {
		return this;
	}

}
