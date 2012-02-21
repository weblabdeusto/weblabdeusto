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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.dto.users;

public class PermissionParameter {

	private String name;
	private String datatype;
	private String value;
	
	public PermissionParameter(String name, String datatype, String value) {
		super();
		this.name = name;
		this.datatype = datatype;
		this.value = value;
	}
	
	public String getName() {
		return this.name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public String getDatatype() {
		return this.datatype;
	}
	public void setDatatype(String datatype) {
		this.datatype = datatype;
	}
	public String getValue() {
		return this.value;
	}
	public void setValue(String value) {
		this.value = value;
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof PermissionParameter )
			return this.name == ((PermissionParameter)other).name &&
			   this.datatype == ((PermissionParameter)other).datatype &&
			   this.value == ((PermissionParameter)other).datatype;
		else
			return false;
	}
}
