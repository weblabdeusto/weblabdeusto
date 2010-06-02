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

package es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb;

import java.util.ArrayList;

import es.deusto.weblab.client.dto.users.Group;

public class AdminPanelWindowHelper {

	public ArrayList<Group> extractGroupsTreeToList(ArrayList<Group> tree) {
		ArrayList<Group> list = new ArrayList<Group>();
		extractGroupsTreeToListRecursively(tree, list);
		return list;
	}	
	
	private void extractGroupsTreeToListRecursively(ArrayList<Group> tree, ArrayList<Group> list) {
		for ( Group group: tree ) {
			list.add(group);
			if ( group.getChildren().size() > 0 ) {
				extractGroupsTreeToListRecursively(group.getChildren(), list);
			}
		}
	}
	
}
