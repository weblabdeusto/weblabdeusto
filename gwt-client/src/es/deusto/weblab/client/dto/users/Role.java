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

public class Role {
	
	private String name;

	public Role() {}
	
	public Role(String name) {
		super();
		this.name = name;
	}

	public String getName() {
		return this.name;
	}
	public void setName(String name) {
		this.name = name;
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof Role ) {
			return this.name.equals(((Role)other).name);
		} else {
			return false;
		}
		
	}
}

