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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.admin.ui.themes.es.deusto.weblab.defaultweb;

import com.google.gwt.core.client.JavaScriptObject;
import com.smartgwt.client.data.Record;
import com.smartgwt.client.widgets.form.DynamicForm;

public class PermissionDetailsDynamicForm extends DynamicForm {

	private long userId;
	private Record userPermissionRecord;
	
	public PermissionDetailsDynamicForm() {
		super();
	}

	public void setUserPermissionRecord(Record userPermissionRec)
	{
		this.userPermissionRecord = userPermissionRec;
	}
	
}
