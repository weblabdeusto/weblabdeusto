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

package es.deusto.weblab.client.dto.experiments;

public class EmptyResponseCommand extends ResponseCommand {

	public EmptyResponseCommand() {
		super(null);
	}

	@Override
	public String getCommandString() {
		throw new IllegalStateException("Illegal state: asking getCommandString in an EmptyResponseCommand");
	}

	@Override
	public boolean isEmpty() {
		return true;
	}
	
	@Override
	public boolean equals(Object o){
		return o instanceof EmptyResponseCommand;
	}
}
