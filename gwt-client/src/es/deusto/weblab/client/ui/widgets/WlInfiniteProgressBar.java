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

package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.google.GlProgressBar;

/**
 * An infinite progress bar is a progress bar whose displayed progress gets 
 * updated automatically at a uniform speed. When the progress reaches the end, 
 * a new cycle starts again. 
 * Infinite progress bars are used to indicate some kind of processing is 
 * being done, when accurate information about the length or real progress of that
 * processing is not available.
 * 
 * Note that WlInfiniteProgressBar appearance highly depends on CSS styles.
 */
public class WlInfiniteProgressBar extends GlProgressBar implements IWlWidget{

	private static final int DEFAULT_CYCLE_TIME = 2000;
	private static final int DEFAULT_RESOLUTION = 10;
	private static final String DEFAULT_PROGRESSBAR_TEXT = "Please, wait...";
	
	// Time in milliseconds that a full load of the bar will take
	private int cycleTime = DEFAULT_CYCLE_TIME;
	
	// Number of times per cycle that the bar will be updated. If set to a low value, such as
	// 10, the bar will update in a rather discrete-looking way.
	private int resolution = DEFAULT_RESOLUTION;
	
	// Time between ticks. Will depend on the cycleTime and the resolution.
	private int updateTime;
	
	// Whether the bar is running.
	private boolean running;
	
	// If true, the bar is in reverse mode. The progress will go back and forth.
	private boolean reverseMode = false;
	
	
	private String progressBarText = DEFAULT_PROGRESSBAR_TEXT;
	private boolean nowOnReverseCycle = false;
	private int counter;
	private Timer currentTimer = null;
	
	
	/**
	 * Creates a new infinite progress bar. By default it will not be started.
	 * 
	 * @see start
	 */
	public WlInfiniteProgressBar(){
		this.running = false;
		this.counter = 0;
		this.setTextVisible(true);
		this.setFixedLengthBarMode(true);
		this.setSegmentWidth(0.2);
	}
	
	/**
	 * Sets the reverse mode.
	 * @param enabled If true, the progress bar will go back and forth. If false,
	 * the progress bar will reset to 0 after being filled.
	 */
	public void setReverseMode(boolean enabled) {
		this.reverseMode = enabled;
		
		if(enabled == false)
			this.nowOnReverseCycle = false;
	}
	
	@Override
	/**
	 * Overrideable function through which the text displayed on the progress bar 
	 * is set.
	 * 
	 * @param see setText
	 */
	protected String generateText(double progress) {
		return this.progressBarText;
	}
	
	/**
	 * Sets the text to display.
	 * 
	 * @param text Text to display within the bar
	 */
	public void setText(String text) {
		this.progressBarText = text;
	}
	
	/**
	 * Retrieves the text that is being displayed.
	 * 
	 * @return Text currently displayed within the bar
	 */
	public String getText() {
		return this.progressBarText;
	}
	
	
	/**
	 * Defines the speed bar. Note that changes to this parameter will not take effect
	 * until start() is called or re-called.
	 * @param cycleTime Milliseconds it takes for the progress bar to go from
	 * empty to full. 
	 */
	public void setCycleTime(int cycleTime) {
		this.cycleTime = cycleTime;
	}
	
	/**
	 * Retrieves the cycle time.
	 * @return In milliseconds, the time it takes for the bar to go from empty to
	 * full.
	 */
	public int getCycleTime() {
		return this.cycleTime;
	}
	
	/**
	 * Sets the resolution of the bar. Note that changes to this parameter will not take
	 * effect until start() is called or re-called.
	 * @param resolution Number of discrete updates to be done before the bar 
	 * is full. If set to 10 for instance, the bar will behave as if it was divided in
	 * ten discrete slots. Given the limitations of the JavaScript animation system
	 * that the bar uses, high resolutions are not recommended.
	 */
	public void setResolution(int resolution) {
		this.resolution = resolution;
	}
	
	/**
	 * Retrieves the resolution of the bar.
	 * @return Number of discrete updates that will be needed before the bar is full.
	 */
	public int getResolution() {
		return this.resolution;
	}
	
	
	/**
	 * Starts animating the progress bar. Parameters should have been set before starting,
	 * if the default values do not fit the case. If the bar is running already, start will
	 * stop it and start it again. This may be useful for getting new parameters to take
	 * effect.
	 * 
	 * @see stop
	 */
	public void start(){
		
		if(this.running == true)
			this.stop();
		
		this.running = true;
		this.setMaxProgress(this.resolution);
		this.setMinProgress(0);
		this.updateTime = this.cycleTime / this.resolution;

		
		this.currentTimer = new Timer(){
			@Override
			public void run(){
				if(WlInfiniteProgressBar.this.running) {
					try {
						WlInfiniteProgressBar.this.process();
					} catch(Throwable th) {
						WlInfiniteProgressBar.this.currentTimer.cancel();
					}
				}
			}
		};
		this.currentTimer.scheduleRepeating(this.updateTime);
	}
	
	
	/**
	 * Will set the bar's progress according to the animation parameters.
	 */
	private void process(){
		this.counter++;
		
		if(this.counter > this.resolution) {
			WlInfiniteProgressBar.this.counter = 0;
			if(this.reverseMode)
				this.nowOnReverseCycle = !this.nowOnReverseCycle;
		}
		
		if(this.nowOnReverseCycle)
			this.setProgress(this.resolution - this.counter);
		else
			this.setProgress(this.counter);

	}

	/**
	 * Stops running the bar. 
	 * When the bar stops it will remain at the state it is in.
	 * 
	 * @see setProgressPercent
	 */
	public void stop(){
		if(this.running){
			if(this.currentTimer != null)
				this.currentTimer.cancel();
			
			this.currentTimer = null;
			this.running = false;
		}
	}
	
	/**
	 * Sets the progress bar as specified. This is not recommended
	 * while the bar is running because it won't generally last long.
	 * 
	 * @param progress Progress of the bar. 0 is an empty bar, 1 is a full bar.
	 */
	public void setProgressPerone(double progress) {
		final double newProg = (this.getMaxProgress() - this.getMinProgress()) * progress;
		this.setMaxProgress(newProg);
	}
	
	@Override
	/**
	 * Gets a reference to oneself.
	 * @return Reference to oneself.
	 */
	public Widget getWidget() {
		return this;
	}

	@Override
	/**
	 * Cleans up the control. Stops the timer if it is running.
	 */
	public void dispose() {
		this.stop();
	}
}
