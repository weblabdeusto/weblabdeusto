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
* Author: FILLME
*
*/

package es.deusto.weblab.client.lab.experiments;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import es.deusto.weblab.client.configuration.FakeConfiguration;

public class ExperimentFactoryResetter {
	public static void reset(){
		EntryRegistry.entries.clear();
		final Map<String, String> globalConfiguration = new HashMap<String, String>();
		final Map<String, List<Map<String, String>>> experimentsConfiguration = new HashMap<String, List<Map<String, String>>>();
		
		experimentsConfiguration.put("xilinx", createXilinxConfig());
		experimentsConfiguration.put("dummy",  createSingleMap("ud-dummy","Dummy experiments"));
		experimentsConfiguration.put("gpib",   createSingleMap("ud-gpib","GPIB experiments"));
		experimentsConfiguration.put("gpib1",  createSingleMap("ud-gpib1","GPIB experiments"));
		experimentsConfiguration.put("gpib2",  createSingleMap("ud-gpib2","GPIB experiments"));
		
		final FakeConfiguration configuration = new FakeConfiguration(globalConfiguration, experimentsConfiguration);
		try{
			ExperimentFactory.loadExperiments(configuration);
		}catch(Exception e){
			e.printStackTrace();
			throw new AssertionError("Unexpected exception raised: " + e.getMessage());
		}
	}
	
	private static List<Map<String, String>> createXilinxConfig(){
		final List<Map<String, String>> xilinxExperiments = new Vector<Map<String, String>>();
		xilinxExperiments.add(createMap("ud-pld","PLD experiments"));
		xilinxExperiments.add(createMap("ud-fpga","FPGA experiments"));
		return xilinxExperiments;
	}
	
	private static List<Map<String, String>> createSingleMap(String experimentName, String experimentCategory){
		final List<Map<String, String>> singleMap = new Vector<Map<String, String>>();
		singleMap.add(createMap(experimentName, experimentCategory));
		return singleMap;
	}
	
	private static Map<String, String> createMap(String experimentName, String experimentCategory){
		final Map<String, String> map = new HashMap<String, String>();
		map.put("experiment.name",     experimentName);
		map.put("experiment.category", experimentCategory);
		return map;
	}
	
}
