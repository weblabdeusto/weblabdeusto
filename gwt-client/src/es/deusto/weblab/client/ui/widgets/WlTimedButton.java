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

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.audio.AudioManager;
import es.deusto.weblab.client.ui.widgets.WlButton.IWlButtonUsed;
import es.deusto.weblab.client.ui.widgets.exceptions.WlWidgetException;

public class WlTimedButton extends VerticalPanel implements IWlWidget{

	public static int DEFAULT_TIME = 1000;
	
	private final WlButton button;
	private final WlIntegerTextbox textbox;
	private final VerticalPanel visiblePanel;
	private final WlActionListenerContainer actionListenerContainer;
	private int time;
	
	private final Label titleLabel = new Label();
	
	public WlTimedButton(){
		this(WlTimedButton.DEFAULT_TIME);
	}

	public WlTimedButton(int time){
		
		this.button = new WlButton();
		this.button.setTime(time);
		this.textbox = new WlIntegerTextbox();
		this.textbox.setText(new Integer(time));
		this.time = time;
		
		this.actionListenerContainer = new WlActionListenerContainer();
		
		this.visiblePanel = this;
		this.setWidth("100%"); 
		this.visiblePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.visiblePanel.add(this.titleLabel);
		this.visiblePanel.add(this.button.getWidget());
		this.visiblePanel.add(this.textbox.getWidget());

		this.button.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				WlTimedButton.this.fireActionListeners();
				AudioManager.getInstance().playBest("snd/switch");
			}
		});
		
		this.textbox.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				final int intValue;
				try {
					intValue = WlTimedButton.this.textbox.getValue().intValue();
					AudioManager.getInstance().playBest("snd/switch");
				} catch (final WlWidgetException e) {
					return;
				}
				WlTimedButton.this.time = intValue;
				WlTimedButton.this.button.setTime(intValue);
			}
		});
		
	}
	
	
	@Override
	public String getTitle() {
		return this.titleLabel.getText();
	}
	
	@Override
	public void setTitle(String title) {
		this.titleLabel.setText(title);
	}
	
	@Override
	public void dispose(){
		this.button.dispose();
		this.textbox.dispose();
	}
	
	public void addActionListener(IWlActionListener listener){
		this.actionListenerContainer.addActionListener(listener);
	}
	
	public void removeActionListener(IWlActionListener listener){
		this.actionListenerContainer.removeActionListener(listener);
	}
	
	public void addButtonListener(IWlButtonUsed listener){
		this.button.addButtonListener(listener);
	}
	
	protected void fireActionListeners(){
		this.actionListenerContainer.fireActionListeners(this);
	}
	
	public int getTime(){
		return this.time;
	}
	
	@Override
	public Widget getWidget() {
		return this.visiblePanel;
	}
}
