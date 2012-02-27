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

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.ErrorEvent;
import com.google.gwt.event.dom.client.ErrorHandler;
import com.google.gwt.event.dom.client.LoadEvent;
import com.google.gwt.event.dom.client.LoadHandler;
import com.google.gwt.user.client.Random;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public class WlWebcam extends VerticalPanel implements IWlWidget{
	
	private static enum WebcamFormat {
		jpeg,
		mjpeg
	}
	
	private static Map<WebcamFormat, String> NAMES = new HashMap<WebcamFormat, String>();
	
	static {
		NAMES.put(WebcamFormat.jpeg, "jpg");
		NAMES.put(WebcamFormat.mjpeg, "video (mjpeg)");
		
		if(NAMES.size() != WebcamFormat.values().length)
			System.err.println("Error: missing value for " + WebcamFormat.class.getName());
	}
	
	public static final String DEFAULT_IMAGE_URL = GWT.getModuleBaseURL() + "/waiting_url_image.jpg";
	public static final int DEFAULT_REFRESH_TIME = 400;
	
	private final Image image;
	
	private final int time;
	private String url;
	private String streamingUrl;
	private Timer timer;
	private boolean running;
	private WebcamFormat currentWebcam = WebcamFormat.jpeg;
	private HorizontalPanel choicePanel;
	
	public WlWebcam(){
		this(WlWebcam.DEFAULT_REFRESH_TIME, WlWebcam.DEFAULT_IMAGE_URL);
	}
	
	public WlWebcam(int time){
		this(time, WlWebcam.DEFAULT_IMAGE_URL);
	}
	
	public WlWebcam(int time, String url){
		this(time, url, WlWebcam.DEFAULT_IMAGE_URL);
	}
	
	public WlWebcam(int time, String url, String streamingUrl){
		final HorizontalPanel imagePanel = new HorizontalPanel();
		imagePanel.setWidth("100%");
		imagePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.time = time;
		this.url          = url;
		this.streamingUrl = streamingUrl;
		
		this.image = new Image(this.getDifferentUrl());
		
		imagePanel.add(this.image);
		this.setWidth("100%");
		this.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.add(imagePanel);
		this.choicePanel = new HorizontalPanel();
		this.choicePanel.setWidth("160px");
		this.choicePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.add(this.choicePanel);
	}
	
	public void start(){
		this.running = true;
		this.timer = new Timer(){
			@Override
			public void run(){
				WlWebcam.this.reload();
			}
		};
		this.reload();
	}
	
	public void stop(){
		this.running = false;
		if(this.timer != null)
			this.timer.cancel();
	}
	
	@Override
	public void dispose(){
		this.running = false;
		
		if(this.timer != null)
			this.timer.cancel();
		
		this.timer = null;
	}
	
	@Override
	public void setVisible(boolean visible){
		super.setVisible(visible);
		this.image.setVisible(visible);
	}
	
	public void reload(){
		if(this.running){
			switch(this.currentWebcam) {
				case jpeg:
					reloadJpeg();
					break;
				case mjpeg:
					reloadMJpeg();
					break;
			}
		}
	}

	private void reloadMJpeg() {
		if(this.image.getUrl() != this.streamingUrl)
			this.image.setUrl(this.streamingUrl);
	}

	private void reloadJpeg() {
		this.image.setUrl(this.getDifferentUrl());
		this.image.addErrorHandler(new ErrorHandler() {
		    
		    @Override
		    public void onError(ErrorEvent event) {
		    	if(WlWebcam.this.timer != null)
		    		WlWebcam.this.timer.schedule(WlWebcam.this.time);
		    }
		});
		this.image.addLoadHandler(new LoadHandler(){
				@Override
				public void onLoad(LoadEvent event) {
					if(WlWebcam.this.timer != null)
						WlWebcam.this.timer.schedule(WlWebcam.this.time);
				}
			}
		);
	}
	
	private String randomStuff(){
		return "?" + Random.nextInt();
	}
	
	private String getDifferentUrl(){
		return this.url + this.randomStuff();
	}

	public String getUrl() {
		return this.url;
	}

	public String getStreamingUrl() {
		return this.streamingUrl;
	}
	
	private void reloadPanel(WebcamFormat format) {
		final List<WebcamFormat> possibleFormats = new Vector<WebcamFormat>();
		if(this.url != DEFAULT_IMAGE_URL) {
			possibleFormats.add(WebcamFormat.jpeg);
		}
		if(this.streamingUrl != DEFAULT_IMAGE_URL) {
			possibleFormats.add(WebcamFormat.mjpeg);
		}

		if(format != null)
			this.currentWebcam = format;
		else if(possibleFormats.size() > 0)
			this.currentWebcam = possibleFormats.get(0);

		this.choicePanel.clear();
		if(possibleFormats.size() > 1) {
			for(final WebcamFormat webcam : possibleFormats) {
				final Widget anchor;
				if(webcam.equals(this.currentWebcam)) {
					anchor = new HTML("<b>" + NAMES.get(webcam) + "</b>");
				} else {
					anchor = new Anchor(NAMES.get(webcam));
					((Anchor)anchor).addClickHandler(new ClickHandler() {
						@Override
						public void onClick(ClickEvent event) {
							reloadPanel(webcam);
						}
					});
				}
				this.choicePanel.add(anchor);
			}
		}
		reload();
		if(this.image.getWidth() > 0)
			this.choicePanel.setWidth((this.image.getWidth() / 2) + "px");
	}

	/**
	 * Sets the URL to obtain the webcam image from and reloads the webcam
	 * so as to display that new image.
	 * @param url URL of the image.
	 */
	public void setUrl(String url) {
		this.url = url;
		this.reloadPanel(null);
	}
	
	/**
	 * Sets the URL to obtain the webcam image in MJPEG format so it 
	 * automatically shows the video stream.
	 * @param url URL of the image.
	 */
	public void setStreamingUrl(String streamingUrl) {
		this.streamingUrl = streamingUrl;
		this.reloadPanel(null);
	}
	
	@Override
	public Widget getWidget(){
		return this;
	}
}
