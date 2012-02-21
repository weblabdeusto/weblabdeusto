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
package es.deusto.weblab.client.lab.controller;


public abstract class PetitionNode {
	
	protected IPetitionFinishedCallback callback = null;
	
	public void start(){
		this.request();
	}
	
	protected abstract void request();
	
	public void addCallback(IPetitionFinishedCallback callback){
		this.callback = callback;
	}
}
