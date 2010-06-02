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

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.dto.users.Group;


public class AdminPanelWindowHelperTest extends GWTTestCase {
	
	public void testExtractGroupsTreeToList() {
		AdminPanelWindowHelper helper = new AdminPanelWindowHelper();
		
		Group group1 = new Group("group 1");
		Group group11 = new Group("group 1.1");
		Group group12 = new Group("group 1.2");
		Group group121 = new Group("group 1.2.1");
		Group group2 = new Group("group 2");
		ArrayList<Group> tree = new ArrayList<Group>();
		group12.addChild(group121);
		group1.addChild(group11);
		group1.addChild(group12);
		tree.add(group1);
		tree.add(group2);
		
		ArrayList<Group> list = helper.extractGroupsTreeToList(tree);
		
		Assert.assertEquals(5, list.size());
		
		Assert.assertEquals(group1, list.get(0));
		Assert.assertEquals(group11, list.get(1));
		Assert.assertEquals(group12, list.get(2));
		Assert.assertEquals(group121, list.get(3));
		Assert.assertEquals(group2, list.get(4));
	}

	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}

}
