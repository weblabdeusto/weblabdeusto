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
	
}
