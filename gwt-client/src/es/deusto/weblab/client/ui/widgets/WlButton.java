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

import java.util.Iterator;
import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Image;

import es.deusto.weblab.client.ui.audio.AudioManager;

public class WlButton extends WlWidgetWithPressable{
	
	public static final String DEFAULT_BUTTON_PRESSED_IMAGE = GWT.getModuleBaseURL() + "img/button_pressed.png";
	public static final String DEFAULT_BUTTON_RELEASED_IMAGE = GWT.getModuleBaseURL() + "img/button.png";
	public static final int    DEFAULT_TIME = 5000; //milliseconds
	
	private final Image       pressedImage;
	private final Image       releasedImage;
	private IWlButtonUsed buttonUsed = null;
	
	private final List<UtilTimer> currentTimers = new Vector<UtilTimer>();
	
	private int time;
	
	public interface IWlButtonUsed{
		public void onPressed();
		public void onReleased();
	}
	
	public WlButton(){
		this(WlButton.DEFAULT_TIME, WlButton.DEFAULT_BUTTON_PRESSED_IMAGE, WlButton.DEFAULT_BUTTON_RELEASED_IMAGE);
	}
	
	public WlButton(int milliseconds){
		this(milliseconds, WlButton.DEFAULT_BUTTON_PRESSED_IMAGE, WlButton.DEFAULT_BUTTON_RELEASED_IMAGE);
	}
	
	public WlButton(int milliseconds, String buttonPressedImageUrl, String buttonReleasedImageUrl){
		this.time = milliseconds;
		
		this.pressedImage = new Image(buttonPressedImageUrl);
		this.releasedImage = new Image(buttonReleasedImageUrl);
		
		this.releasedImage.addClickHandler(new ClickHandler() {
			@Override
			public void onClick(ClickEvent sender) {
				WlButton.this.buttonPressed();
				WlButton.this.fireActionListeners();
			}
		});
		
		this.setOldImage(this.pressedImage);
		this.setCurrentVisibleImage(this.releasedImage);
	}
	
	protected void buttonPressed(){
		this.press();
		if(WlButton.this.buttonUsed != null) {
			WlButton.this.buttonUsed.onPressed();
			AudioManager.getInstance().playBest("snd/button");
		}
		
		final UtilTimer timer = new UtilTimer(){
			@Override
			public void realRun(){
				WlButton.this.press();
				if(WlButton.this.buttonUsed != null) {
					WlButton.this.buttonUsed.onReleased();
					AudioManager.getInstance().playBest("snd/button");
				}
			}
		};
		
		timer.schedule(this.time);
		this.addTimer(timer);
	}
	
	private void addTimer(UtilTimer timer){
		this.cleanOldTimers();
		this.currentTimers.add(timer);
	}
	
	private void cleanOldTimers(){
		final Iterator<UtilTimer> it = this.currentTimers.iterator();
		while(it.hasNext()){
			final UtilTimer t = it.next();
			if(t.hasBeenRun())
				it.remove();
		}
	}
	
	private void cancelTimers(){
		final Iterator<UtilTimer> it = this.currentTimers.iterator();
		while(it.hasNext()){
			final UtilTimer t = it.next();
			t.cancel();
		}
		this.currentTimers.clear();
	}
	
	@Override
	public void dispose(){
		this.cleanOldTimers();
		this.cancelTimers();
	}
	
	public void addButtonListener(IWlButtonUsed buttonUsed){
		this.buttonUsed = buttonUsed;
	}

	public int getTime() {
		return this.time;
	}

	public void setTime(int time) {
		this.time = time;
	}
	
	/*
	 * The Timer class provided by GWT does not tell us whether
	 * the method has been already called or not.
	 */
	private abstract class UtilTimer extends Timer{
		
		private boolean bhasBeenRun = false;
		
		public abstract void realRun();
		
		@Override
		public void run(){
			this.bhasBeenRun = true;
			this.realRun();
		}
		
		public boolean hasBeenRun(){
			return this.bhasBeenRun;
		}
	}
}
