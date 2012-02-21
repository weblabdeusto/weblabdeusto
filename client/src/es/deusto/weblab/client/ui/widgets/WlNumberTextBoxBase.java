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
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Widget;

import es.deusto.weblab.client.ui.widgets.exceptions.WlInvalidValueException;
import es.deusto.weblab.client.ui.widgets.exceptions.WlWidgetException;

public abstract class WlNumberTextBoxBase implements IWlWidget{
	
	public static final String DEFAULT_PLUS_PRESSED_IMAGE   = GWT.getModuleBaseURL() + "img/add_pressed.png";
	public static final String DEFAULT_PLUS_RELEASED_IMAGE  = GWT.getModuleBaseURL() + "img/add.png";
	public static final String DEFAULT_MINUS_PRESSED_IMAGE  = GWT.getModuleBaseURL() + "img/subtract_pressed.png";
	public static final String DEFAULT_MINUS_RELEASED_IMAGE = GWT.getModuleBaseURL() + "img/subtract.png";
	public static final int    DEFAULT_TEXT_LENGTH          = 4;
	public static final int    PRESSED_TIME                 = 100;
	
	private final WlButton minusButton;
	private Class<?> numberType;
	private final WlButton plusButton;
	private HorizontalPanel visiblePanel;
	
	private final WlActionListenerContainer actionListenerContainer;
	
	public WlNumberTextBoxBase(Class<?> numberType){
		this(WlNumberTextBoxBase.DEFAULT_PLUS_PRESSED_IMAGE, WlNumberTextBoxBase.DEFAULT_PLUS_RELEASED_IMAGE, WlNumberTextBoxBase.DEFAULT_MINUS_PRESSED_IMAGE, WlNumberTextBoxBase.DEFAULT_MINUS_RELEASED_IMAGE);
		this.numberType = numberType;
	}
	
	public WlNumberTextBoxBase(String plusPressedImageUrl, String plusReleasedImageUrl, String minusPressedImageUrl, String minusReleasedImageUrl){
		
		this.actionListenerContainer = new WlActionListenerContainer();
		this.plusButton = new WlButton(WlNumberTextBoxBase.PRESSED_TIME, plusPressedImageUrl, plusReleasedImageUrl);
		this.minusButton = new WlButton(WlNumberTextBoxBase.PRESSED_TIME, minusPressedImageUrl, minusReleasedImageUrl);
		
		this.plusButton.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget) {
				Number numberValue;
				try {
					numberValue = WlNumberTextBoxBase.this.getValue();
				} catch (final WlWidgetException e) {
					//Can't add if the value is not an integer
					return;
				}
				final Number increasedValue = WlNumberTextBoxBase.this.nextValue(numberValue);
				WlNumberTextBoxBase.this.setText(increasedValue);
				WlNumberTextBoxBase.this.fireActionListeners();
			}
		});
		
		this.minusButton.addActionListener(new IWlActionListener(){
			@Override
			public void onAction(IWlWidget widget){
				Number numberValue;
				try {
					numberValue = WlNumberTextBoxBase.this.getValue();
				} catch (final WlWidgetException e) {
					//Can't add if the value is not an integer
					return;
				}
				final Number decreasedValue = WlNumberTextBoxBase.this.previousValue(numberValue);
				WlNumberTextBoxBase.this.setText(decreasedValue);
				WlNumberTextBoxBase.this.fireActionListeners();
			}
		});
	}
	
	protected void configure(){
		this.visiblePanel = new HorizontalPanel();
		this.visiblePanel.add(this.minusButton.getWidget());
		this.visiblePanel.add(this.getTextWidget());
		this.visiblePanel.add(this.plusButton.getWidget());
	}
	
	@Override
	public void dispose(){
		this.plusButton.dispose();
		this.minusButton.dispose();
	}

	public void addActionListener(IWlActionListener listener){
		this.actionListenerContainer.addActionListener(listener);
	}
	
	public void removeActionListener(IWlActionListener listener){
		this.actionListenerContainer.removeActionListener(listener);
	}
	
	protected void fireActionListeners(){
		this.actionListenerContainer.fireActionListeners(this);
	}
	
	protected abstract Number nextValue(Number intValue);
	protected abstract Number previousValue(Number intValue);
	protected abstract HasText getHasText();
	protected abstract Widget getTextWidget();
	
	public void setLength(int length){
	    final String formattedLength = (length * 10) + "px";
	    // XXX: this can't be used until bug 4772 of GWT is fixed:
	    //   http://code.google.com/p/google-web-toolkit/issues/detail?id=4772
	    // final String formattedLength = length + "em";
		this.getTextWidget().setWidth(formattedLength);
	}
	
	public void setText(Number n){
		this.getHasText().setText(n.toString());
	}
	
	public Number getValue() throws WlWidgetException{
		if(this.numberType.equals(Integer.class)){
			try {
				return new Integer(Integer.parseInt(this.getHasText().getText()));
			} catch (final NumberFormatException e) {
				throw new WlInvalidValueException("Invalid value: " + this.getHasText().getText());
			}
		}else if(this.numberType.equals(Float.class)){
			try {
				return new Float(Float.parseFloat(this.getHasText().getText()));
			} catch (final NumberFormatException e) {
				throw new WlInvalidValueException("Invalid value: " + this.getHasText().getText());
			}
		}else{
			try {
				return new Double(Double.parseDouble(this.getHasText().getText()));
			} catch (final NumberFormatException e) {
				throw new WlInvalidValueException("Invalid value: " + this.getHasText().getText());
			}
		}
	}
	
	@Override
	public Widget getWidget() {
		return this.visiblePanel;
	}	
}
