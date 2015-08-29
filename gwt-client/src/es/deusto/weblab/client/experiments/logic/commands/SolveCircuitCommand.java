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

package es.deusto.weblab.client.experiments.logic.commands;

import java.util.List;
import java.util.Vector;

import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.experiments.logic.circuit.Circuit;
import es.deusto.weblab.client.experiments.logic.circuit.Gate;
import es.deusto.weblab.client.experiments.logic.circuit.Operation;

public class SolveCircuitCommand extends Command {

    private final Operation [] operations;
    
    public SolveCircuitCommand(Circuit circuit) {
	final List<Operation> lOperations = new Vector<Operation>();
	for(final Gate gate : circuit.getUnknownOperations())
	    lOperations.add(gate.getOperation());
	
	this.operations = lOperations.toArray(new Operation[]{});
    }

    @Override
    public String getCommandString() {
	String name = "SOLVE ";
	for(final Operation operation : this.operations){
	    name += operation.getName() + " ";
	}
	return name;
    }

}
