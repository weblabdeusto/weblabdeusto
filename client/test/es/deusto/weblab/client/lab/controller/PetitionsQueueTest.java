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

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.lab.controller.PetitionNode;
import es.deusto.weblab.client.lab.controller.PetitionsQueue;
import es.deusto.weblab.client.lab.controller.petitions.CommandPetition;
import es.deusto.weblab.client.lab.controller.petitions.GuiImagePetition;
import es.deusto.weblab.client.lab.controller.petitions.PollPetition;
import es.deusto.weblab.client.lab.controller.petitions.TimePetition;
import es.deusto.weblab.client.lab.controller.petitions.WebcamImagePetition;

public class PetitionsQueueTest extends GWTTestCase {
	PetitionsQueue queue;
	
	@Override
	public void gwtSetUp(){
		this.queue = new PetitionsQueue();
	}
	
	public void testPetitionsQueueIgnoringMoreThanOneWebcamImage(){
		for(int i = 0; i < 5; ++i)
			this.queue.push(new WebcamImagePetition());
		
		PetitionNode petition = this.queue.pop();
		Assert.assertNotNull(petition);
		Assert.assertTrue(petition instanceof WebcamImagePetition);
		
		//Next petition is null
		petition = this.queue.pop();
		Assert.assertNull(petition);
	}
	
	public void testPetitionsQueueIgnoringMoreThanOnePoll(){
		for(int i = 0; i < 5; ++i)
			this.queue.push(new PollPetition());
		
		PetitionNode petition = this.queue.pop();
		Assert.assertNotNull(petition);
		Assert.assertTrue(petition instanceof PollPetition);
		
		//Next petition is null
		petition = this.queue.pop();
		Assert.assertNull(petition);
	}
	
	public void testPetitionsQueueIgnoringMoreThanOneTime(){
		for(int i = 0; i < 5; ++i)
			this.queue.push(new TimePetition());
		
		PetitionNode petition = this.queue.pop();
		Assert.assertNotNull(petition);
		Assert.assertTrue(petition instanceof TimePetition);
		
		//Next petition is null
		petition = this.queue.pop();
		Assert.assertNull(petition);
	}
	
	public void testPetitionsQueueCommandsNotIgnored(){
		final int NUM = 5;
		final CommandPetition [] commands = new CommandPetition[NUM];
		for(int i = 0; i < NUM; ++i){
			commands[i] = new CommandPetition();
			this.queue.push(commands[i]);
		}
		for(int i = 0; i < NUM; ++i){
			final PetitionNode node = this.queue.pop();
			Assert.assertNotNull(node);
			Assert.assertTrue(node instanceof CommandPetition);
			Assert.assertEquals(node, commands[i]);
		}
		final PetitionNode node = this.queue.pop();
		Assert.assertNull(node);
	}
	
	public void testPetitionsQueueGuiImagesNotIgnored(){
		final int NUM = 5;
		final GuiImagePetition [] images = new GuiImagePetition[NUM];
		for(int i = 0; i < NUM; ++i){
			images[i] = new GuiImagePetition();
			this.queue.push(images[i]);
		}
		for(int i = 0; i < NUM; ++i){
			final PetitionNode node = this.queue.pop();
			Assert.assertNotNull(node);
			Assert.assertTrue(node instanceof GuiImagePetition);
			Assert.assertEquals(node, images[i]);
		}
		final PetitionNode node = this.queue.pop();
		Assert.assertNull(node);
	}
	
	public void testPetitionsQueuePollsIgnoredIfCommandFound(){
		PollPetition poll = new PollPetition();
		this.queue.push(poll);
		CommandPetition command = new CommandPetition();
		this.queue.push(command);
		
		PetitionNode node = this.queue.pop();
		Assert.assertNotNull(node);
		Assert.assertTrue(node instanceof CommandPetition);
		node = this.queue.pop();
		Assert.assertNull(node);
		
		poll = new PollPetition();
		command = new CommandPetition();
		this.queue.push(command);
		this.queue.push(poll);
		
		node = this.queue.pop();
		Assert.assertNotNull(node);
		Assert.assertTrue(node instanceof CommandPetition);
		node = this.queue.pop();
		Assert.assertNull(node);
	}
	
	public void testPetitionsQueueOrder(){
		//Order from most important to least important: 
		//Poll > Gui Image  > Command > Time > Webcam Image
		
		// Poll > Gui Image
		PetitionNode node;
		
		this.queue.push(new GuiImagePetition());
		this.queue.push(new PollPetition());
		
		node = this.queue.pop();
		Assert.assertTrue(node instanceof PollPetition);
		node = this.queue.pop();
		Assert.assertTrue(node instanceof GuiImagePetition);
		node = this.queue.pop();
		Assert.assertNull(node);
		
		// Gui Image > Command
		this.queue.push(new CommandPetition());
		this.queue.push(new GuiImagePetition());
		
		node = this.queue.pop();
		Assert.assertTrue(node instanceof GuiImagePetition);
		node = this.queue.pop();
		Assert.assertTrue(node instanceof CommandPetition);
		node = this.queue.pop();
		Assert.assertNull(node);
		
		// Command > Time
		this.queue.push(new TimePetition());
		this.queue.push(new CommandPetition());
		
		node = this.queue.pop();
		Assert.assertTrue(node instanceof CommandPetition);
		node = this.queue.pop();
		Assert.assertTrue(node instanceof TimePetition);
		node = this.queue.pop();
		Assert.assertNull(node);
		
		// Time > WebcamImage
		this.queue.push(new WebcamImagePetition());
		this.queue.push(new TimePetition());
		
		node = this.queue.pop();
		Assert.assertTrue(node instanceof TimePetition);
		node = this.queue.pop();
		Assert.assertTrue(node instanceof WebcamImagePetition);
		node = this.queue.pop();
		Assert.assertNull(node);
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
