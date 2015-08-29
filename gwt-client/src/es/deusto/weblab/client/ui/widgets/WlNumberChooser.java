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
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Widget;

public class WlNumberChooser extends WlNumberTextBoxBase {

	public static final Number [] DEFAULT_ALLOWED_VALUES   = new Number[]{
			new Integer(250),
			new Integer(500),
			new Integer(1000),
			new Integer(1500),
			new Integer(2000)
		};
	public static final Number DEFAULT_VALUE               = new Integer(1000);
	
	private final Number [] allowedValues;
	private final Label label;

	public WlNumberChooser(Class<?> numberType){
		this(WlNumberTextBoxBase.DEFAULT_TEXT_LENGTH, WlNumberChooser.DEFAULT_ALLOWED_VALUES, WlNumberChooser.DEFAULT_VALUE, numberType);
	}
	
	public WlNumberChooser(int length, Number [] allowedValues, Number defaultValue, Class<?> numberType){
		super(numberType);
		
		this.allowedValues = allowedValues;
		
		this.label = new Label();
		this.label.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		
		this.setLength(length);
		
		this.setText(defaultValue);
		
		super.configure();
	}

	@Override
	public Number nextValue(Number numberValue){
		for(int i = 0; i < this.allowedValues.length - 1; ++i)
			if(this.allowedValues[i].equals(numberValue))
				return this.allowedValues[i + 1];
		return numberValue;
	}
	
	@Override
	public Number previousValue(Number numberValue){
		for(int i = 1; i < this.allowedValues.length; ++i)
			if(this.allowedValues[i].equals(numberValue))
				return this.allowedValues[i - 1];
		return numberValue;
	}

	@Override
	protected HasText getHasText() {
		return this.label;
	}
	
	@Override
	protected Widget getTextWidget() {
		return this.label;
	}
}
