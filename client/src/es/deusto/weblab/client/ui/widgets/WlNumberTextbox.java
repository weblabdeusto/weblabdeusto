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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/ 
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.TextBoxBase;
import com.google.gwt.user.client.ui.Widget;

public abstract class WlNumberTextbox extends WlNumberTextBoxBase {

	protected Number differenceValue;
	protected TextBox textBox;
	
	protected abstract boolean isDigit(char keyCode);
	public abstract Number  getMaxValue();
	public abstract Number  getMinValue();
	
	public WlNumberTextbox(int length, Number difference, Number defaultValue, Class<?> numberType){
		super(numberType);
		
		this.differenceValue = difference;
		
		this.textBox = new TextBox();
		this.textBox.setTextAlignment(TextBoxBase.ALIGN_CENTER);
		this.setLength(length);
		
		this.setText(defaultValue);
		
		this.textBox.addKeyPressHandler(new KeyPressHandler(){

		    	public void onKeyPress(KeyPressEvent event) {
				if(!WlNumberTextbox.this.isDigit(event.getCharCode()) && !WlNumberTextbox.this.isMoveKey(event.getCharCode()))
					((TextBox)event.getSource()).cancelKey();
			}
		});
		
		this.textBox.addChangeHandler(new ChangeHandler() {
			public void onChange(ChangeEvent sender) {
				WlNumberTextbox.this.fireActionListeners();
			}
		});
		
		super.configure();
	}
	
	private boolean isMoveKey(char keyCode) {
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
