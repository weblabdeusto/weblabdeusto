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
*         Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/ 
package es.deusto.weblab.client.dto.users;

import java.util.ArrayList;

public class User extends Agent {
	
	private String login;
	private String fullName;
	private String email;
	private Role role;
	private String adminUrl;
	private ArrayList<Group> groups;
	
	public User() {}

	public User(String login, String fullName, String email, Role role, String adminUrl) {
		super();
		this.login = login;
		this.fullName = fullName;
		this.email = email;
		this.role = role;
		this.adminUrl = adminUrl;
		this.groups = new ArrayList<Group>();
	}	
	
	public String getAdminUrl() {
		return this.adminUrl;
	}
	
	public String getLogin() {
		return this.login;
	}
	public void setLogin(String login) {
		this.login = login;
	}
	public String getFullName() {
		return this.fullName;
	}
	public void setFullName(String fullName) {
		this.fullName = fullName;
	}
	public String getEmail() {
		return this.email;
	}
	public void setEmail(String email) {
		this.email = email;
	}	
	public Role getRole() {
		return this.role;
	}
	public void setRole(Role role) {
		this.role = role;
	}
	
	public void addToGroup(Group group) {
		// Be careful with the circular references!
		this.groups.add(group);
		group.addUser(this);
	}
	
	public boolean isMemberOf(Group group) {
		return this.groups.contains(group);
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof User ) {
			return this.login.equals(((User)other).login);
		} else {
			return false;
		}
		
	}	
}
