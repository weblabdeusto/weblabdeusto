/*
* Copyright (C) 2012 onwards University of Deusto
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

package es.deusto.weblab.client.dto;

public class NullSessionID extends SessionID {

	public NullSessionID() {
		super("");
	}

	@Override
	public boolean isNull() {
		return true;
	}

}
