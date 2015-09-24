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

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyDownEvent;
import com.google.gwt.event.dom.client.KeyDownHandler;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.ui.ValueBoxBase.TextAlignment;

public abstract class WlNumberTextbox extends WlNumberTextBoxBase {

	protected Number differenceValue;
	protected TextBox textBox;
	
	protected abstract boolean isDigit(int keyCode);
	public abstract Number  getMaxValue();
	public abstract Number  getMinValue();
	
	public WlNumberTextbox(int length, Number difference, Number defaultValue, Class<?> numberType){
		super(numberType);
		
		this.differenceValue = difference;
		
		this.textBox = new TextBox();
		this.textBox.setAlignment(TextAlignment.CENTER);
		this.setLength(length);
		
		this.setText(defaultValue);
		
		this.textBox.addKeyDownHandler(new KeyDownHandler(){
		    	@Override
				public void onKeyDown(KeyDownEvent event) {
				if(!WlNumberTextbox.this.isDigit(event.getNativeKeyCode()) && !WlNumberTextbox.this.isMoveKey(event.getNativeKeyCode()))
					((TextBox)event.getSource()).cancelKey();
			}
		});
		
		this.textBox.addChangeHandler(new ChangeHandler() {
			@Override
			public void onChange(ChangeEvent sender) {
				WlNumberTextbox.this.fireActionListeners();
			}
		});
		
		super.configure();
	}
	
	private boolean isMoveKey(int keyCode) {
		switch (keyCode) {
			case KeyCodes.KEY_CTRL:
			case KeyCodes.KEY_DELETE:
			case KeyCodes.KEY_ALT:
			case KeyCodes.KEY_BACKSPACE:
			case KeyCodes.KEY_DOWN:
			case KeyCodes.KEY_END:
			case KeyCodes.KEY_HOME:
			case KeyCodes.KEY_LEFT:
			case KeyCodes.KEY_ENTER:
			case KeyCodes.KEY_ESCAPE:
			case KeyCodes.KEY_PAGEDOWN:
			case KeyCodes.KEY_PAGEUP:
			case KeyCodes.KEY_RIGHT:
			case KeyCodes.KEY_SHIFT:
			case KeyCodes.KEY_TAB:
			case KeyCodes.KEY_UP:
				return true;
			default:
				return false;
		}
	}

	@Override
	protected HasText getHasText() {
		return this.textBox;
	}

	@Override
	protected Widget getTextWidget() {
		return this.textBox;
	}
}
