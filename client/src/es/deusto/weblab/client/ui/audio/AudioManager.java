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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.ui.audio;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AudioElement;
import com.google.gwt.media.client.Audio;


public class AudioManager {
	
	private static final AudioManager instance = new AudioManager();
	
	private boolean soundEnabled = false;
	
	/**
	 * Retrieves the only instance of this class thay may exist.
	 * @return The one instance of the AudioManager class.
	 */
	public static AudioManager getInstance() { 
		return AudioManager.instance;
	}
	
	/**
	 * Checks whether sounds are enabled. If they are not, no sound at all
	 * should ever be played.
	 * @return True if sounds are enabled. False otherwise.
	 */
	public boolean getSoundEnabled() {
		return this.soundEnabled;
	}
	
	/**
	 * Enables or disables sound.
	 * @param enable True to enable, false to disable.
	 */
	public void setSoundEnabled(boolean enable) {
		this.soundEnabled = enable;
	}
	
	
	/**
	 * Helper method which will play a sound if certain conditions are met:
	 * Sound is enabled.
	 * Sound is supported.
	 * File type is supported.
	 * If they are not, calling this method will have no effect.
	 * @param file File to play. The path should be relative to the module base URL.
	 * 
	 * @return AudioElement being played, or null. May be used to modify the default behaviour, such
	 * as enabling loop mode.
	 */
	public AudioElement play(String file) {
		if( this.getSoundEnabled() ) {
			final Audio audio = Audio.createIfSupported();
			if( audio != null ) {
				final AudioElement elem = audio.getAudioElement();
				elem.setSrc(GWT.getModuleBaseURL() + file);
				elem.play();
				return elem;
			}
		}
		return null;
	}
	
	
}
