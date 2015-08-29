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


public class PetitionsController implements IPetitionsController {
	
	private final PetitionsQueue queue;
	private boolean running;
	
	public PetitionsController(){
		this.queue = new PetitionsQueue();
		this.running = false;
	}
	
	@Override
	public void push(PetitionNode node){
		this.queue.push(node);
		if(!this.running)
			this.processNext();
	}
	
	private void processNext(){
		final PetitionNode node = this.queue.pop();
		if(node != null){
			node.addCallback(new IPetitionFinishedCallback(){
				@Override
				public void onLoaded() {
					PetitionsController.this.running = false;
					PetitionsController.this.processNext();
				}
			});
			this.running = true;
			node.start();
		}//else: no petition was found in the queue
	}
}
