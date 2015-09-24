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

package es.deusto.weblab.client.experiments.logic.circuit;

public class Circuit {
    
    private final Gate root;
    private final Gate [] unknowns;
    
    public Circuit(Gate input){
	this.root = input;
	
	/// XXX: At the moment there is only one unknown
	this.unknowns = new Gate[1];
	this.unknowns[0] = (Gate)this.root.getLeft().getRight();
    }
    
    public Operation getUnknownOperation(int n){
	return this.unknowns[n].getOperation();
    }
    
    public void setUnknownOperation(int n, Operation operation){
	this.unknowns[n].setOperation(operation);
    }
    
    public Gate [] getUnknownOperations(){
	return this.unknowns;
    }
    
    public Gate getRoot(){
	return this.root;
    }
}
