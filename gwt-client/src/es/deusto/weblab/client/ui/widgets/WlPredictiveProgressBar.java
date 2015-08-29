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


import java.util.Date;

import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.DOM;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.google.GlProgressBar;

/**
 * A predictive progress bar is a progress bar which which indicates the
 * estimated progress of some process. Because that progress is simply
 * an estimation, the predictive progress bar updates itself automatically
 * depending only on the time elapsed (and on the estimated time before
 * completion, which can be configured). 
 * 
 * Optionally, it is possible to
 * specify a single wait-point. If set, the bar's automatic progress will
 * stop upon reaching that point, until it is notified that it may continue.
 * That way if the estimation was not accurate, and the real progress
 * is slower than anticipated the user will know that the process has not
 * finished yet.  
 * 
 * Note that WlPredictiveProgressBar appearance depends on CSS styles.
 */
public class WlPredictiveProgressBar extends GlProgressBar implements IWlWidget {
	
	public static final String COLOR_RED = "#F0C0C0";
	public static final String COLOR_BLUE = "#C0C0F0";
	public static final String COLOR_GREEN = "#C0F0C0";
	
	private static final float DEFAULT_WAIT_POINT = 0.9f;
	
	private static final int DEFAULT_RESOLUTION = 10;
	
	private static final int DEFAULT_ESTIMATED_TIME = 10000;
	
	// Total time it will probably take, in ms
	private int estimatedTime = DEFAULT_ESTIMATED_TIME;
	
	// Time at which the bar was started
	private long startTime;
	
	// Updater that will be used to generate the text that will be displayed, 
	// if any.
	private IProgressBarTextUpdater textUpdater = new DefaultProgressBarTextUpdater();

	// Listener that will be notified whenever certain events occur.
	private IProgressBarListener listener = null;
	
	// Point at which the bar will stop and wait until notified (0 to 1).
	private double waitPoint = DEFAULT_WAIT_POINT;

	// Number of times per full cycle that the bar will be updated. If set to a low value, such as
	// 10, the bar will update in a rather discrete-looking way.
	private int resolution = DEFAULT_RESOLUTION;
	
	// Time between ticks. Will depend on the cycleTime and the resolution.
	private int updateTime;
	
	// Whether the bar is running.
	private boolean running;
	
	// What is the original segment width when using setFixedLengthBarMode
	private double originalSegmentWidth;
	
	private boolean waiting = false;
	private int counter;
	private Timer currentTimer = null;
	
	
	/**
	 * Interface which will receive an event whenever the progress changes,
	 * and which can be used to customize the text of the progress bar, and
	 * for other purposes.
	 */
	public static interface IProgressBarTextUpdater {
		/**
		 * Generates the text that will be displayed.
		 * @param progress Progress, from 0 to 1
		 * @return Text to display
		 */
		public String generateText(double progress);
	}
	
	/**
	 * This updater will simply display the progress, truncating it
	 * to no decimals. This is the default updater.
	 */
	public static class DefaultProgressBarTextUpdater implements IProgressBarTextUpdater {
		@Override
		public String generateText(double progress) {
			return (int)Math.round(progress * 100) + "%";
		}
	}
	
	/**
	 * This updater will simply display the specified sentence. This sentence may be changed.
	 */
	public static class TextProgressBarTextUpdater implements IProgressBarTextUpdater {
		
		protected String str;
		
		/**
		 * Creates a TextProgressBarTextUpdater.
		 * @param str String to display on the progress bar.
		 * @see setString
		 */
		public TextProgressBarTextUpdater(String str) {
			this.str = str;
		}
		
		/**
		 * Sets a new string, which will start being displayed on the
		 * next cycle.
		 * @param str String to display on the progress bar
		 */
		public void setString(String str) {
			this.str = str;
		}
		
		/**
		 * Gets the string that is to be displayed.
		 * @return String to display.
		 */
		public String getString() {
			return this.str;
		}
		
		@Override
		public String generateText(double progress) {
			return this.str;
		}
		
	}
	

	/**
	 * Interface which provides certain callbacks which may
	 * be useful for the PredictiveProgressBar users.
	 */
	public interface IProgressBarListener {
		
		/**
		 * Will be invoked whenever the progress reaches 100%.
		 * Note that if displaying progress is explicitly 
		 * disabled on the progress bar this method might not work
		 * as expected.
		 */
		void onFinished();
	}
	
	
	/**
	 * Creates a new predictive progress bar. By default it will not be started.
	 * Note that the estimated time is initialized to 10.000 ms. 
	 * 
	 * @see start
	 * @see setEstimatedTime
	 */
	public WlPredictiveProgressBar(){
		this.running = false;
		this.counter = 0;
		this.setTextVisible(true);
		this.setSegmentWidth(0.2);
		
		this.setEstimatedTime(this.estimatedTime);
	}
	
	
	@Override
	/**
	 * Uses the updater to generate the text that is to be
	 * displayed. If the updater is null, the default GlProgressBar
	 * updater will be used.
	 * @param progress Progress so far, from 0 to 1
	 */
	protected String generateText(double progress) {
		
		// Convert the progress to a per-one.
		final double progressPercent = progress / this.getMaxProgress();
		
		String text = null;
		if(this.textUpdater != null) 
			text = this.textUpdater.generateText(progressPercent);

		if(text == null)
			text = super.generateText(progressPercent);

		if( progressPercent >= 1.0 )
			this.stop();
		
		return text;
	}
	
	/**
	 * Checks whether the bar is running. 
	 * @return True if running, false otherwise.
	 */
	public boolean isRunning() {
		return this.running;
	}
	
	/**
	 * Sets the updater that will be used to generate the text to
	 * display in the progress bar. The text will be updated instantly.
	 * That is, just after setting it, the text updater will be called 
	 * to generate new text.
	 * @param textUpdater Updater
	 */
	public void setTextUpdater(IProgressBarTextUpdater textUpdater) {
		this.textUpdater = textUpdater;
		this.setProgress(this.getProgress());
	}
	
	
	/**
	 * Specifies a listener which will be notified whenever
	 * certain events occur. If set to null, any current listener
	 * will be discarded.
	 * @param listener Listener which whose callbacks will be invoked
	 */
	public void setListener(IProgressBarListener listener) {
		this.listener = listener;
	}
	
	/**
	 * Retrieves the updater that will be used to generate the text to 
	 * display in the progress bar
	 * @return Updater
	 */
	public IProgressBarTextUpdater getTextUpdater() {
		return this.textUpdater;
	}
	
	/**
	 * Sets the estimated time that the process will probably
	 * take to complete.
	 * @param estimatedTime Estimated time, in milliseconds
	 */
	public void setEstimatedTime(int estimatedTime) {
		this.estimatedTime = estimatedTime;
	}
	
	/**
	 * Retrieves the estimated time that the process will probably
	 * take to complete. 
	 * @return Estimated time in milliseconds
	 * @see setEstimatedTime
	 */
	public int getEstimatedTime() {
		return this.estimatedTime;
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
	 * Sets the wait point .
	 * @param point Point, from 0 to 1, that we want to set as wait point.
	 */
	public void setWaitPoint(double point) {
		this.waitPoint = point;
	}
	
	
	/**
	 * Retrieves the resolution of the bar.
	 * @return Number of discrete updates that will be needed before the bar is full.
	 */
	public int getResolution() {
		return this.resolution;
	}
	
	
	/**
	 * Resets the elapsed time measurement timer.
	 * @see getElapsedTime
	 * @see start
	 */
	public void resetTimer() {
		this.startTime = new Date().getTime();
	}
	
	/**
	 * Gets the number of miliseconds elapsed since
	 * start was called or the timer was reset.
	 * @see resetTimer
	 * @see start
	 */
	public long getElapsedTime() {
		if(this.startTime == 0)
			return 0;
		return new Date().getTime() - this.startTime;
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
		
		resetTimer();
		this.running = true;
		this.setMaxProgress(this.resolution);
		this.setMinProgress(0);
		this.updateTime = (int)((double)this.estimatedTime / this.resolution);

		
		this.currentTimer = new Timer(){
			@Override
			public void run(){
				if(WlPredictiveProgressBar.this.running) {
					try {
						WlPredictiveProgressBar.this.process();
					} catch(Throwable th) {
						if(WlPredictiveProgressBar.this.currentTimer != null)
							WlPredictiveProgressBar.this.currentTimer.cancel();
					}
				}
			}
		};
		

		this.currentTimer.scheduleRepeating(this.updateTime);
	}
	
	/**
	 * Keeps waiting showing the progress bar moving
	 */
	public void keepWaiting(){
		if(this.currentTimer != null)
			this.currentTimer.cancel();
		
		this.running = true;
		this.waiting = true;
		this.counter = 0;
		setFixedLengthBarMode(true);
		this.originalSegmentWidth = getSegmentWidth();
		
		this.currentTimer = new Timer(){
			@Override
			public void run(){
				processWaiting();
			}
		};
		
		this.currentTimer.scheduleRepeating(50);
		processWaiting();
	}
	
	public boolean isWaiting(){
		return this.waiting;
	}
	
	private void processWaiting(){
		this.counter++;
		final double total = (double) this.counter / this.resolution;
		
		if(this.counter >= this.resolution){
			this.counter = 0;
			setSegmentWidth(0);
			setProgress(this.counter);
		}else{
			if(total < this.originalSegmentWidth)
				setSegmentWidth(total);
			else
				setSegmentWidth(this.originalSegmentWidth);
			
			setProgress(this.counter);
		}
	}
	
	
	
	/**
	 * Will make the bar reach end in the specified number of ms. WaitPoint will be set to 1.
	 * Note that if the bar is already running, the previous kind of updating will stop.
	 * 
	 * @param ms Number of milliseconds that it will take the bar to reach the end
	 * @see progressTo
	 */
	public void finish(int ms) {
		this.progressTo(1.0f, ms);
	}
	
	
	
	
	 
	/**
	 * Will make the bar progress from the current point until it reaches the
	 * specified one. Will set the wait point to the value of the target point,
	 * because the progress bar will stop just there. If the progress bar is currently
	 * running, the previous kind of updating will stop.
	 * 
	 * @param point Point, from 0 to 1, that the progress bar should reach
	 * @param ms Number of milliseconds that it will take the bar to reach the end
	 */
	public void progressTo(double point, int ms) {
		if(this.currentTimer == null) // Already stopped
			return;
		
		this.currentTimer.cancel();

		// Get current discrete progress.
		double cur = this.getProgress();
		
		// Get target discrete progress.
		double target = (this.getMaxProgress() - this.getMinProgress()) * point;
		
		// Get the number of discrete updates we will have to carry out
		double missingUpdates = target - cur;
		
		// Get the number of ms we will need to put between updates for the desired resolution
		int period = (int) (ms / missingUpdates);
		
		this.currentTimer.scheduleRepeating(period);
		this.running = true;
		
		// Otherwise the wait point can't be surpased
		this.setWaitPoint(point);
	}
	
	
	/**
	 * Will set the bar's progress according to the animation parameters.
	 */
	private void process() {
		this.counter++;
		
		this.setProgress(this.counter);
		
		if(this.getPercent() > this.waitPoint) {
			this.setProgressPerone(this.waitPoint);
			this.currentTimer.cancel();
			this.running = false;
		}
	}
	
	@Override
	public void setProgress(double progress) {
		super.setProgress(progress);
		
		if(this.listener != null && this.getPercent() >= 1.0)
			this.listener.onFinished();
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
		this.setProgress(newProg);
	}
	
	
	/**
	 * Sets the bar's color.
	 * @param color A string with the hex color in the #RRGGBB format.
	 */
	public void setBarColor(String color) {
		final Element elem = this.getBarElement();
		DOM.setStyleAttribute(elem, "backgroundColor", color);
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
