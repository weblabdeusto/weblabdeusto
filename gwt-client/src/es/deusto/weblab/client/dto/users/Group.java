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

import java.util.ArrayList;

public class Group {

	private int id;
	private String name;
	private Group parent;
	private final ArrayList<Group> children;
	private final ArrayList<User> users;
	
	public Group(String name) {
		super();
		this.name = name;
		this.parent = null;
		this.children = new ArrayList<Group>();
		this.users = new ArrayList<User>();
	}
	
	public Group(int id, String name, ArrayList<Group> children) {
		super();
		this.id = id;
		this.name = name;
		this.parent = null;
		this.children = children;
		this.users = new ArrayList<User>();
	}
	
	public int getId() {
		return this.id;
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
	private void setParent(Group parent) {
		this.parent = parent;
	}

	public ArrayList<Group> getChildren() {
		return this.children;
	}

	public String getFullName() {
		if ( this.parent == null ) {
			return this.name;
		} else {
			return this.parent.getFullName() + " > " + this.name;
		}
	}
	
	public void addChild(Group group) {
		group.setParent(this);
		this.children.add(group);
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
