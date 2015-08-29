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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

package es.deusto.weblab.client.experiments.gpib.commands;

import es.deusto.weblab.client.dto.experiments.Command;

public class ResultFileCommand extends Command {

	public ResultFileCommand() {}

	@Override
	public String getCommandString() {
		return "RESULT file";
	}
}
