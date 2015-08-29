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
*
*/ 
package es.deusto.weblab.client;

import com.google.gwt.core.client.EntryPoint;

public abstract class WebLabClient implements EntryPoint {
    
	public static String baseLocation;
	
	@Override
	public void onModuleLoad() {
		this.baseLocation = ""; // TODO
	}
}
