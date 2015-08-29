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

public class Gate implements IInput{
    
    private IInput left;
    private IInput right;
    private Operation operation;
    
    public Gate(IInput left, IInput right, Operation operation){
	this.left      = left;
	this.right     = right;
	this.operation = operation;
    }

    @Override
   public IInput getLeft() {
        return this.left;
    }

    public void setLeft(IInput left) {
        this.left = left;
    }

    @Override
    public IInput getRight() {
        return this.right;
    }

    public void setRight(IInput right) {
        this.right = right;
    }

    @Override
    public Operation getOperation() {
        return this.operation;
    }

    public void setOperation(Operation operation) {
        this.operation = operation;
    }
}
