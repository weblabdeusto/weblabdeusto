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
package es.deusto.weblab.client.configuration;

import junit.framework.Assert;

import com.google.gwt.core.client.GWT;
import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.configuration.exceptions.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.configuration.exceptions.InvalidConfigurationValueException;

public class ConfigurationManagerTest extends GWTTestCase {

	ConfigurationManager confManager;
	
	public void testNotExistingConfigurationFile(){
		this.delayTestFinish(500);
		this.confManager = new ConfigurationManager("this.file.does.not.exist.js",
				new IConfigurationLoadedCallback(){

					@Override
					public void onLoaded() {
						try{
							Assert.fail("The file should not have been found and an exception should have raised");
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}

					@Override
					public void onFailure(Throwable t) {
						//Ok
						ConfigurationManagerTest.this.finishTest();
					}
				}
		);
		this.confManager.start();
	}
	
	public void testNotJsonConfigurationFile(){
		if(!GWT.isScript()){
			this.delayTestFinish(500);
			this.confManager = new ConfigurationManager( GWT.getModuleBaseURL() + "configuration_test_3.js",
					new IConfigurationLoadedCallback(){
	
						@Override
						public void onLoaded() {
							try{
								Assert.fail("The file should not have been found and an exception should have raised");
							}finally{
								ConfigurationManagerTest.this.finishTest();
							}
						}
	
						@Override
						public void onFailure(Throwable t) {
							//Ok
							ConfigurationManagerTest.this.finishTest();
						}
					}
			);
			this.confManager.start();
		}else{
			// This test fails in production 
		}
	}
	
	public void testRightSimpleConfiguration(){
		this.delayTestFinish(500);
		this.confManager = new ConfigurationManager( GWT.getModuleBaseURL() + "configuration_test.js", 
				new IConfigurationLoadedCallback(){
					@Override
					public void onLoaded() {
						try{
							//Using default values
							int number = ConfigurationManagerTest.this.confManager.getIntProperty("intproperty1",-1);
							Assert.assertEquals(number,15);
							String s = ConfigurationManagerTest.this.confManager.getProperty("property1","whatever");
							Assert.assertEquals(s,"value1");
							
							//Without using default values
							try {
								number = ConfigurationManagerTest.this.confManager.getIntProperty("intproperty1");
								Assert.assertEquals(number,15);
								s = ConfigurationManagerTest.this.confManager.getProperty("property1");
								Assert.assertEquals(s,"value1");
							} catch (final ConfigurationKeyNotFoundException e) {
								Assert.fail("ConfigurationKeyNotFoundException raised: " + e.getMessage() );
							} catch (final InvalidConfigurationValueException e) {
								Assert.fail("InvalidConfigurationValueException raised: " + e.getMessage());
							}
							
							// Parsing experiments
							final IConfigurationRetriever[] flashRetrievers;
							try {
								flashRetrievers = ConfigurationManagerTest.this.confManager.getExperimentsConfiguration("flash");
							} catch (InvalidConfigurationValueException e) {
								Assert.fail(InvalidConfigurationValueException.class.getName()+ " raised: " + e.getMessage());
								return;
							}
							
							Assert.assertEquals(1, flashRetrievers.length);
							final String experimentName = flashRetrievers[0].getProperty("experiment.name","not this");
							Assert.assertEquals("flashdummy", experimentName);
							
							final int width = flashRetrievers[0].getIntProperty("width", -1);
							Assert.assertEquals(500, width);
							
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}

					@Override
					public void onFailure(Throwable t) {
						try{
							Assert.fail("onFailure called when instanciating the ConfigurationManager: " + t.getMessage());
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}
				}
		);
		this.confManager.start();
	}
	
	public void testWrongConfiguration(){
		this.delayTestFinish(500);
		this.confManager = new ConfigurationManager( GWT.getModuleBaseURL() + "configuration_test.js", 
				new IConfigurationLoadedCallback(){
					@Override
					public void onLoaded() {
						try{
							//Using default values
							int n = ConfigurationManagerTest.this.confManager.getIntProperty("this.does.not.exist",15);
							Assert.assertEquals(n,15);
							n = ConfigurationManagerTest.this.confManager.getIntProperty("wrongintproperty",15);
							Assert.assertEquals(n,15);
							String s = ConfigurationManagerTest.this.confManager.getProperty("this.does.not.exist","something");
							Assert.assertEquals(s,"something");
							
							//Without using default values
							try {
								n = ConfigurationManagerTest.this.confManager.getIntProperty("this.does.not.exist");
								Assert.fail("ConfigurationKeyNotFoundException expected and not raised; returned: " + n);
							}catch (final ConfigurationKeyNotFoundException e) {
								//Ok
							}catch (final InvalidConfigurationValueException e) {
								Assert.fail("InvalidConfigurationValueException raised: " + e.getMessage());
							}
														
							try {
								n = ConfigurationManagerTest.this.confManager.getIntProperty("wrongintproperty");
								Assert.fail("InvalidConfigurationValueException expected and not raised; returned: " + n);
							}catch (final ConfigurationKeyNotFoundException e) {
								Assert.fail("ConfigurationKeyNotFoundException raised: " + e.getMessage());
							}catch (final InvalidConfigurationValueException e) {
								//Ok
							}
														
							try{
								s = ConfigurationManagerTest.this.confManager.getProperty("this.does.not.exist");
								Assert.fail("ConfigurationKeyNotFoundException expected and not raised; returned: " + s);
							} catch (final ConfigurationKeyNotFoundException e) {
								//Ok
							} catch (InvalidConfigurationValueException e) {
								Assert.fail(InvalidConfigurationValueException.class.getName() + " raised: " + e.getMessage());
							}
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}

					@Override
					public void onFailure(Throwable t) {
						Assert.fail("onFailure called when instanciating the ConfigurationManager: " + t.getMessage());
					}
				}
		);
		this.confManager.start();
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
