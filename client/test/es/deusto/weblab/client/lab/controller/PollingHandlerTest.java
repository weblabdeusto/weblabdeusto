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

import java.util.List;
import java.util.Vector;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;
import es.deusto.weblab.client.lab.controller.IPetitionsController;
import es.deusto.weblab.client.lab.controller.PetitionNode;

public class PollingHandlerTest extends GWTTestCase  {
	
	final static int TEST_POLLING_TIME = 10;
	
	class FakeConfigurationManager implements IConfigurationManager{

		@Override
		public int getIntProperty(String key) throws ConfigurationKeyNotFoundException, InvalidConfigurationValueException {
			throw new IllegalStateException("getIntProperty(String) should not be called");
		}

		@Override
		public int getIntProperty(String key, int def) {
			return PollingHandlerTest.TEST_POLLING_TIME;
		}

		@Override
		public String getProperty(String key) throws ConfigurationKeyNotFoundException {
			throw new IllegalStateException("getProperty(String) should not be called");
		}

		@Override
		public String getProperty(String key, String def) {
			throw new IllegalStateException("getProperty(String, String) should not be called");
		}
		
		@Override
		public boolean getBoolProperty(String key) {
			throw new IllegalStateException("getBoolProperty(String) should not be called");
		}			
		
		@Override
		public boolean getBoolProperty(String key, boolean def) {
			throw new IllegalStateException("getBoolProperty(String, boolean) should not be called");
		}

		@Override
		public IConfigurationRetriever[] getExperimentsConfiguration(
				String experimentType)
				throws InvalidConfigurationValueException {
			throw new IllegalStateException("getExperimentsConfiguration(String) should not be called");
		}		
	}
	
	class FakePetitionsController implements IPetitionsController{
		List<PetitionNode> pushedNodes = new Vector<PetitionNode>();
		@Override
		public void push(PetitionNode node) {
			this.pushedNodes.add(node);
		}
	}
	
	public void testPollingHandler(){
		//ConfigurationManager confManager = new FakeConfigurationManager();
		//FakePetitionsController petitions = new FakePetitionsController();
		
		//PollingHandler pollHandler = new PollingHandler(confManager, petitions);
		//pollHandler.start();
		//TODO test pollinghandler
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
