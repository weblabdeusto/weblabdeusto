/*
* Copyright (C) 2005-2009 University of Deusto
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

import es.deusto.weblab.client.exceptions.configuration.ConfigurationKeyNotFoundException;
import es.deusto.weblab.client.exceptions.configuration.InvalidConfigurationValueException;

public class ConfigurationManagerTest extends GWTTestCase {

	ConfigurationManager confManager;
	
	public void testNotExistingConfigurationFile(){
		this.delayTestFinish(500);
		this.confManager = new ConfigurationManager("this.file.does.not.exist.js",
				new IConfigurationLoadedCallback(){

					public void onLoaded() {
						try{
							Assert.fail("The file should not have been found and an exception should have raised");
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}

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
	
						public void onLoaded() {
							try{
								Assert.fail("The file should not have been found and an exception should have raised");
							}finally{
								ConfigurationManagerTest.this.finishTest();
							}
						}
	
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
					public void onLoaded() {
						try{
							//Using default values
							int dato = ConfigurationManagerTest.this.confManager.getIntProperty("intproperty1",-1);
							Assert.assertEquals(dato,15);
							String s = ConfigurationManagerTest.this.confManager.getProperty("property1","whatever");
							Assert.assertEquals(s,"value1");
							
							//Without using default values
							try {
								dato = ConfigurationManagerTest.this.confManager.getIntProperty("intproperty1");
								Assert.assertEquals(dato,15);
								s = ConfigurationManagerTest.this.confManager.getProperty("property1");
								Assert.assertEquals(s,"value1");
							} catch (final ConfigurationKeyNotFoundException e) {
								Assert.fail("ConfigurationKeyNotFoundException raised: " + e.getMessage() );
								e.printStackTrace();
							} catch (final InvalidConfigurationValueException e) {
								Assert.fail("InvalidConfigurationValueException raised: " + e.getMessage());
								e.printStackTrace();
							}
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}
					public void onFailure(Throwable t) {
						Assert.fail("onFailure called when instanciating the ConfigurationManager: " + t.getMessage());
					}
				}
		);
		this.confManager.start();
	}
	
	public void testWrongConfiguration(){
		this.delayTestFinish(500);
		this.confManager = new ConfigurationManager( GWT.getModuleBaseURL() + "configuration_test.js", 
				new IConfigurationLoadedCallback(){
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
								e.printStackTrace();
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
							}
						}finally{
							ConfigurationManagerTest.this.finishTest();
						}
					}

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
