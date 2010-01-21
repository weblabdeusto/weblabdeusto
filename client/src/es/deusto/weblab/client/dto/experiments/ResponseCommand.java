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
* Author: Pablo Orduña <pablo@ordunya.com>
*
*/

package es.deusto.weblab.client.dto.experiments;

public class ResponseCommand extends Command {

	private final String commandString;
	
	public ResponseCommand(String commandString) {
		this.commandString = commandString;
	}

	@Override
	public String getCommandString() {
		return this.commandString;
	}

	public boolean isEmpty() {
		return false;
	}
}
