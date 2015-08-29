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

public class Permission {
	
	private String name;
	private PermissionParameter[] parameters;
	
	public Permission(String name, PermissionParameter[] parameters) {
		super();
		this.name = name;
		this.parameters = parameters;
	}
	
	public String getName() {
		return this.name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public PermissionParameter[] getParameters() {
		return this.parameters;
	}
	public void setParameters(PermissionParameter[] parameters) {
		this.parameters = parameters;
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof Permission ) {
			if ( this.name != ((Permission)other).name )
				return false;
			if ( this.parameters.length != ((Permission)other).parameters.length )
				return false;
			for ( int i = 0; i < this.parameters.length; ++i )
				if ( this.parameters[i] != ((Permission)other).parameters[i] )
					return false;
		} else {
			return false;
		}
		return true;
	}
}
