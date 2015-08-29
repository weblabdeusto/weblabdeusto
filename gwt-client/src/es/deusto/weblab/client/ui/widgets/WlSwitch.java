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

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.EventHandler;
import com.google.gwt.event.shared.GwtEvent;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.user.client.ui.Image;

import es.deusto.weblab.client.ui.audio.AudioManager;

public class WlSwitch extends WlWidgetWithPressable {
	
	public static final String DEFAULT_SWITCHED_ON_IMAGE = GWT.getModuleBaseURL() + "img/switch_on.png";
	public static final String DEFAULT_SWITCHED_OFF_IMAGE = GWT.getModuleBaseURL() + "img/switch_off.png";
	
	private final Image switchedOnImage;
	private final Image switchedDownImage;
	private boolean switchedOn;

	public WlSwitch(){
		this(WlSwitch.DEFAULT_SWITCHED_ON_IMAGE,WlSwitch.DEFAULT_SWITCHED_OFF_IMAGE);
	}
	
	public WlSwitch(String switchedOnImageUrl, String switchedOffImageUrl){
		this.switchedOnImage = new Image(switchedOnImageUrl);
		this.switchedDownImage = new Image(switchedOffImageUrl);
		
		final ClickHandler clickListener = new ClickHandler(){
			@Override
			public void onClick(ClickEvent sender) {
				WlSwitch.this.switchedOn = !WlSwitch.this.switchedOn;
				fireEvent(new SwitchEvent(WlSwitch.this.switchedOn));
				WlSwitch.this.press();
				AudioManager.getInstance().playBest("snd/switch");
				WlSwitch.this.fireActionListeners();
			}
		};
		
		this.switchedOnImage.addClickHandler(clickListener);
		this.switchedDownImage.addClickHandler(clickListener);
		
		this.setOldImage(this.switchedOnImage);
		this.setCurrentVisibleImage(this.switchedDownImage);
		this.switchedOn = false;
	}
	
	public HandlerRegistration addClickHandler(SwitchHandler handler) {
	    return addHandler(handler, SwitchEvent.TYPE);
	}
	
	public void switchWithoutFiring(boolean newState) {
		if(newState != this.switchedOn) {
			press();
			this.switchedOn = newState;
		}
	}
	
	@Override
	public void dispose(){}
	
	public boolean isSwitched(){
		return this.switchedOn;
	}
	
	public static interface SwitchHandler extends EventHandler{
		void onClick(SwitchEvent event);
	}
	
	public static class SwitchEvent extends GwtEvent<SwitchHandler> {

		private static final Type<SwitchHandler> TYPE = new Type<SwitchHandler>();
		
		@Override
		public com.google.gwt.event.shared.GwtEvent.Type<SwitchHandler> getAssociatedType() {
			return TYPE;
		}
		
		private boolean on;
		
		public SwitchEvent(boolean on) {
			this.on = on;
		}
		
		public boolean isOn() {
			return this.on;
		}
		
		public boolean isOff() {
			return !this.on;
		}

		@Override
		protected void dispatch(SwitchHandler handler) {
			handler.onClick(this);
		}
		
	}	
}
