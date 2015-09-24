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

public class Switch implements IInput {
    public final boolean turned;
    
    public Switch(boolean turned){
	this.turned = turned;
    }
    
    public boolean isTurned(){
	return this.turned;
    }

    @Override
    public IInput getLeft() {
	throw new IllegalStateException("getLeft not implemented");
    }

    @Override
    public IInput getRight() {
	throw new IllegalStateException("getRight not implemented");
    }

    @Override
    public Operation getOperation() {
	throw new IllegalStateException("getOperation not implemented");
    }
}
