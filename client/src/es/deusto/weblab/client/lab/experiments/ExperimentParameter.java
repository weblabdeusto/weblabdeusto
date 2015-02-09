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

public class ExperimentParameter {
	
	public static enum Type {
		string,
		integer,
		floating,
		bool
	}
	
	private final String name;
	private final Type type;
	private final String description;
	
	public ExperimentParameter(String name, Type type, String description) {
		this.name = name;
		this.type = type;
		this.description = description;
	}

	public String getName() {
		return this.name;
	}

	public Type getType() {
		return this.type;
	}

	public String getDescription() {
		return this.description;
	}
	
	public boolean hasDefaultValue() {
		return false;
	}
	
}
