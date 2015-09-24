/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.experiments;

public class ExperimentParameterDefault extends ExperimentParameter {
	private final Object defaultValue;

	public ExperimentParameterDefault(String name, String description, String defaultValue) {
		super(name, Type.string, description);
		this.defaultValue = defaultValue;
	}
	
	public ExperimentParameterDefault(String name, String description, int defaultValue) {
		super(name, Type.integer, description);
		this.defaultValue = defaultValue;
	}
	
	public ExperimentParameterDefault(String name, String description, double defaultValue) {
		super(name, Type.floating, description);
		this.defaultValue = defaultValue;
	}

	public ExperimentParameterDefault(String name, String description, boolean defaultValue) {
		super(name, Type.bool, description);
		this.defaultValue = defaultValue;
	}
	
	public int getIntDefaultValue() {
		return ((Integer)this.defaultValue).intValue();
	}
	
	public double getDoubleDefaultValue() {
		return ((Double)this.defaultValue).floatValue();
	}
	
	public boolean getBooleanDefaultValue() {
		return ((Boolean)this.defaultValue).booleanValue();
	}
	
	public String getStringDefaultValue() {
		return (String)this.defaultValue;
	}
	
	@Override
	public boolean hasDefaultValue() {
		return true;
	}
}
