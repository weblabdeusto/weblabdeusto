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
* Author: FILLME
*
*/

package es.deusto.weblab.client.dto.users;

import java.util.ArrayList;

public class Group {
	
	private String name;
	private Group parent;
	private ArrayList<User> users;
	
	public Group(String name, Group parent) {
		super();
		this.name = name;
		this.parent = parent;
		this.users = new ArrayList<User>();
	}
	
	public String getName() {
		return this.name;
	}
	public void setName(String name) {
		this.name = name;
	}
	public Group getParent() {
		return this.parent;
	}
	public void setParent(Group parent) {
		this.parent = parent;
	}

	public String getFullName() {
		if ( this.parent == null ) {
			return this.name;
		} else {
			return this.parent.getFullName() + " > " + this.name;
		}
	}
	
	public void addUser(User user) {
		this.users.add(user);
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof Group ) {
			if ( this.parent == null ) {
				return this.name.equals(((Group)other).name);
			} else {
				return this.name.equals(((Group)other).name) && this.parent.equals(((Group)other).parent);	
			}
		} else {
			return false;
		}
		
	}
}
