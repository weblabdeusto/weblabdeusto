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
package es.deusto.weblab.client.experiments.pic.commands;

import es.deusto.weblab.client.dto.experiments.Command;

public class WriteCommand extends Command{
	private final int boxCode;
	private final String text;
	
	public WriteCommand(int boxCode, String text){
		this.boxCode = boxCode;
		this.text    = text;
	}
	
	@Override
	public String getCommandString() {
		return "WRITE=" + this.boxCode + " " + this.text + " EOT";
	}
}
