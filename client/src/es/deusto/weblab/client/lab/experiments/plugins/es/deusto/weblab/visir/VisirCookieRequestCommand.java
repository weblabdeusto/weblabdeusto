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

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.visir;

import es.deusto.weblab.client.dto.experiments.Command;

public class VisirCookieRequestCommand extends Command {

	@Override
	public String getCommandString() {
		return "GIVEMECOOKIE";
	}

}
