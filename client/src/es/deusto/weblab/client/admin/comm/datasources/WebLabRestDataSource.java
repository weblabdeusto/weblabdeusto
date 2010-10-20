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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.admin.comm.datasources;

import java.util.HashMap;

import com.smartgwt.client.data.RestDataSource;
import com.smartgwt.client.types.DSDataFormat;

import es.deusto.weblab.client.dto.SessionID;

public abstract class WebLabRestDataSource extends RestDataSource {
	
	private final SessionID sessionId;

	public WebLabRestDataSource(SessionID sessionId) {
		super();
		
		this.sessionId = sessionId;
	    this.setDataFormat(DSDataFormat.JSON);
	    HashMap<String, String> defaultParams = new HashMap<String, String>();
	    defaultParams.put("sessionid", this.sessionId.getRealId());
	    this.setDefaultParams(defaultParams);
	}
	
	public abstract void initialize();
}
