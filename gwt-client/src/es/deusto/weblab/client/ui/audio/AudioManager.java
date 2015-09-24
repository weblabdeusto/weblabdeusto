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
*
*/

package es.deusto.weblab.client.ui.audio;

import com.google.gwt.core.client.GWT;
import com.google.gwt.dom.client.AudioElement;
import com.google.gwt.dom.client.MediaElement;
import com.google.gwt.media.client.Audio;

import es.deusto.weblab.client.configuration.ConfigurationRetriever;



public class AudioManager {

	private static final String MP3_TYPE = "audio/mpeg;";
	private static final String OGG_TYPE = "audio/ogg; codecs=\"vorbis\"";
	private static final String WAV_TYPE = "audio/wav; codecs=\"1\"";
	

	private static final boolean SOUND_ENABLED_DEFAULT = false;
	private static final String SOUND_ENABLED_NAME = "sound.enabled";
	
	private static AudioManager instance = null;
	
	private ConfigurationRetriever configurationRetriever;
	
	/**
	 * Constructs the AudioManager instance.
	 * @param retriever ConfigurationRetriever which will be stored internally and
	 * which makes it possible to access and modify globally the sound_enabled setting.
	 * 
	 * @see initialize
	 */
	private AudioManager(ConfigurationRetriever retriever) {
		this.configurationRetriever = retriever;
	}
	
	/**
	 * Constructs the only Audio Manager instance. Needs to be called before
	 * being able to retrieve the AudioManager's instance.
	 * It needs to be constructed explicitly because of the retriever
	 * parameter the singleton requires.
	 * 
	 * @param retriever ConfigurationRetriever which will be stored internally
	 * and which makes it possible to access and modify globally the sound_enabled
	 * setting.
	 * 
	 * @throws RuntimeException If the singleton has already been initialized once
	 * and hence an instance exists already.
	 * 
	 * @see getInstance
	 */
	public static void initialize(ConfigurationRetriever retriever) {
		if(instance != null)
			throw new RuntimeException("AudioManager singleton has already been initialized");
		instance = new AudioManager(retriever);
	}
	
	/**
	 * Retrieves the only instance of this class that may exist.
	 * 
	 * @return The one instance of the AudioManager class. Null if the singleton
	 * has not been initialized yet.
	 * 
	 * @see initialize
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
		final boolean enabled = this.configurationRetriever.getBoolProperty(SOUND_ENABLED_NAME, 
				SOUND_ENABLED_DEFAULT);
		return enabled;
	}
	
	/**
	 * Enables or disables sound. 
	 * @param enable True to enable, false to disable.
	 */
	public void setSoundEnabled(boolean enable) {
		this.configurationRetriever.setBoolProperty(SOUND_ENABLED_NAME, enable);
	}
	
	
	/**
	 * Helper method which will play a sound if certain conditions are met:
	 * Sound is enabled.
	 * Sound is supported.
	 * File type is supported.
	 * If they are not, calling this method will have no effect.
	 * @param file File to play. The path should be relative to the module base URL. E.g. "/audio/foo.wav"
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
	
	/**
	 * Helper method which will play a sound if certain conditions are met:
	 * Sound is enabled.
	 * Sound is supported.
	 * If they are not, calling this method will have no effect.
	 * 
	 * The file type is inferred by the web browser. If it supports OGG, it will use the ".ogg" extension. If it doesn't, but it
	 * supports MP3, it will use ".mp3". It will also try WAV, and otherwise it will not work. Therefore, the audio files must be 
	 * duplicated in these three formats to work. 
	 * 
	 * @param file File to play. The path should be relative to the module base URL. E.g. "/audio/foo" will select foo.ogg, foo.mp3 or foo.wav
	 * 
	 * @return AudioElement being played, or null. May be used to modify the default behaviour, such
	 * as enabling loop mode.
	 */
	public AudioElement playBest(String file) {
		if( this.getSoundEnabled() ) {
			final Audio audio = Audio.createIfSupported();
			if( audio != null ) {
				final AudioElement elem = audio.getAudioElement();
				
				// First try probably
				if(elem.canPlayType(OGG_TYPE).equals(MediaElement.CAN_PLAY_PROBABLY))
					elem.setSrc(GWT.getModuleBaseURL() + file + ".ogg");
				else if(elem.canPlayType(MP3_TYPE).equals(MediaElement.CAN_PLAY_PROBABLY))
					elem.setSrc(GWT.getModuleBaseURL() + file + ".mp3");
				else if(elem.canPlayType(WAV_TYPE).equals(MediaElement.CAN_PLAY_PROBABLY))
					elem.setSrc(GWT.getModuleBaseURL() + file + ".wav");
				// Then maybe
				else if(elem.canPlayType(OGG_TYPE).equals(MediaElement.CAN_PLAY_MAYBE))
					elem.setSrc(GWT.getModuleBaseURL() + file + ".ogg");
				else if(elem.canPlayType(MP3_TYPE).equals(MediaElement.CAN_PLAY_MAYBE))
					elem.setSrc(GWT.getModuleBaseURL() + file + ".mp3");
				else if(elem.canPlayType(WAV_TYPE).equals(MediaElement.CAN_PLAY_MAYBE))
					elem.setSrc(GWT.getModuleBaseURL() + file + ".wav");
				// Then fail
				else
					return null;
				
				elem.play();
				return elem;
			}
		}
		return null;
	}
	
	
}
