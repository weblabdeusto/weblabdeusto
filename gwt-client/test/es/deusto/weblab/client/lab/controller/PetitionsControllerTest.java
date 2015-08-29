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

import es.deusto.weblab.client.lab.controller.IPetitionsController;
import es.deusto.weblab.client.lab.controller.PetitionsController;
import es.deusto.weblab.client.lab.controller.petitions.CommandPetitionFake;
import es.deusto.weblab.client.lab.controller.petitions.GuiImagePetitionFake;

public class PetitionsControllerTest extends GWTTestCase{

	public void testPetitionController(){
		final IPetitionsController controller = new PetitionsController();
		
		final CommandPetitionFake commandFake1 = new CommandPetitionFake();
		final CommandPetitionFake commandFake2 = new CommandPetitionFake();
		final GuiImagePetitionFake guiImageFake = new GuiImagePetitionFake();
		
		Assert.assertFalse(commandFake1.wasCalled());
		Assert.assertFalse(commandFake2.wasCalled());
		Assert.assertFalse(guiImageFake.wasCalled());
		
		controller.push(commandFake1);
		controller.push(commandFake2);
		controller.push(guiImageFake);
		
		Assert.assertTrue(commandFake1.wasCalled());
		Assert.assertFalse(commandFake2.wasCalled());
		Assert.assertFalse(guiImageFake.wasCalled());
		
		commandFake1.callCallback();
		
		//guiImage has priority over commandFake2
		Assert.assertTrue(commandFake1.wasCalled());
		Assert.assertFalse(commandFake2.wasCalled());
		Assert.assertTrue(guiImageFake.wasCalled());
		
		guiImageFake.callCallback();
		
		Assert.assertTrue(commandFake1.wasCalled());
		Assert.assertTrue(commandFake2.wasCalled());
		Assert.assertTrue(guiImageFake.wasCalled());
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
