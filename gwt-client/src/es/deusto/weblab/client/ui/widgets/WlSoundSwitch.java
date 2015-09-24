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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
* 		  Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Image;

import es.deusto.weblab.client.ui.audio.AudioManager;


/**
 * Widget whose purpose is to enable or disable sound. It displays a clickable
 * speaker, which changes depending on the selected mode.
 * Based on the WlSwitch.
 */
public class WlSoundSwitch extends WlWidgetWithPressable{
	
	public static final String DEFAULT_SWITCHED_ON_IMAGE = GWT.getModuleBaseURL() + "img/audio_on.png";
	public static final String DEFAULT_SWITCHED_OFF_IMAGE = GWT.getModuleBaseURL() + "img/audio_off.png";
	
	private final Image switchedOnImage;
	private final Image switchedDownImage;
	private boolean switchedOn;

	/**
	 * Constructs the sound switch using the default images to represent the two states.
	 */
	public WlSoundSwitch(){
		this(WlSoundSwitch.DEFAULT_SWITCHED_ON_IMAGE, WlSoundSwitch.DEFAULT_SWITCHED_OFF_IMAGE);
	}
	
	/**
	 * Constructs the sound switch using the specified images.
	 * @param switchedOnImageUrl Image to display when the switch is turned on.
	 * @param switchedOffImageUrl Image to display when the switch is turned off.
	 */
	public WlSoundSwitch(String switchedOnImageUrl, String switchedOffImageUrl){
		this.switchedOnImage = new Image(switchedOnImageUrl);
		this.switchedDownImage = new Image(switchedOffImageUrl);
		
		// Retrieve the current, global sound state.
		this.switchedOn = AudioManager.getInstance().getSoundEnabled();
		
		final ClickHandler clickListener = new ClickHandler(){
			@Override
			public void onClick(ClickEvent sender) {
				WlSoundSwitch.this.switchedOn = !WlSoundSwitch.this.switchedOn;
				WlSoundSwitch.this.press();
				WlSoundSwitch.this.fireActionListeners();
				
				if(WlSoundSwitch.this.switchedOn) {
					// TODO: Replace this by the more extensible method which uses
					// the config javascript itself.
					AudioManager.getInstance().setSoundEnabled(true);
				} else {
					AudioManager.getInstance().setSoundEnabled(false);
				}
			}
		};
		
		this.switchedOnImage.addClickHandler(clickListener);
		this.switchedDownImage.addClickHandler(clickListener);
		
		// Make sure it is initialized to the proper state.
		if(! this.switchedOn) {
			this.setOldImage(this.switchedOnImage);
			this.setCurrentVisibleImage(this.switchedDownImage);
			this.switchedOn = false;
		} else {
			this.setOldImage(this.switchedDownImage);
			this.setCurrentVisibleImage(this.switchedOnImage);
			this.switchedOn = true;
		}
		
	}
	
	
	/**
	 * Sets the width of the images. Can be used as an uibinder
	 * attribute.
	 * 
	 * @param width Width of both images, as a string.
	 */
	public void setImgWidth(String width) {
		this.switchedDownImage.setWidth(width);
		this.switchedOnImage.setWidth(width);
		
		// Force a repaint, which seems to be required.
		if(this.switchedDownImage.isVisible())
			this.switchedDownImage.setVisible(true);
	}
	
	/**
	 * Sets the height of the images. Can be used an uibinder
	 * attribute.
	 * 
	 * @param height Height of both images, as a string.
	 */
	public void setImgHeight(String height) {
		this.switchedDownImage.setHeight(height);
		this.switchedOnImage.setHeight(height);
		
		// Force a repaint, which seems to be required.
		if(this.switchedDownImage.isVisible())
			this.switchedDownImage.setVisible(true);
	}
	
	
	@Override
	public void dispose(){}
	
	public boolean isSwitched(){
		return this.switchedOn;
	}
}
