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

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONString;

public class ExperimentFactoryResetter {
	public static void reset(){
		final JSONObject experimentsConfiguration = new JSONObject();
		
		experimentsConfiguration.put("xilinx", createXilinxConfig());
		experimentsConfiguration.put("dummy",  createSingleMap("ud-dummy","Dummy experiments"));
		experimentsConfiguration.put("gpib",   createSingleMap("ud-gpib","GPIB experiments"));
		experimentsConfiguration.put("gpib1",  createSingleMap("ud-gpib1","GPIB experiments"));
		experimentsConfiguration.put("gpib2",  createSingleMap("ud-gpib2","GPIB experiments"));
		
		try{
			ExperimentFactory.loadExperiments(experimentsConfiguration.toString());
		}catch(Exception e){
			e.printStackTrace();
			throw new AssertionError("Unexpected exception raised: " + e.getMessage());
		}
	}
	
	private static JSONArray createXilinxConfig(){
		final JSONArray xilinxExperiments = new JSONArray();
		xilinxExperiments.set(0, createMap("ud-pld","PLD experiments"));
		xilinxExperiments.set(1, createMap("ud-fpga","FPGA experiments"));
		return xilinxExperiments;
	}
	
	private static JSONArray createSingleMap(String experimentName, String experimentCategory){
		final JSONArray singleMap = new JSONArray();
		singleMap.set(0, createMap(experimentName, experimentCategory));
		return singleMap;
	}
	
	private static JSONObject createMap(String experimentName, String experimentCategory){
		final JSONObject map = new JSONObject();
		map.put("experiment.name",     new JSONString(experimentName));
		map.put("experiment.category", new JSONString(experimentCategory));
		return map;
	}
	
}
