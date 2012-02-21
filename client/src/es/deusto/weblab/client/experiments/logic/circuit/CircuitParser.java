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

import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;

public class CircuitParser {
    
    public Circuit parseCircuit(String serializedCircuit) throws InvalidCircuitException{
	try{
	    final JSONValue value = JSONParser.parseStrict(serializedCircuit);
	    return new Circuit((Gate)this.parseInput(value));
	}catch(final Exception e){
	    throw new InvalidCircuitException("Invalid serialized circuit!" + e.getMessage(), e);
	}
    }
    
    public IInput parseInput(JSONValue value){
	if(value instanceof JSONBoolean)
	    return new Switch(((JSONBoolean)value).booleanValue());
	
	final JSONObject obj = ((JSONObject)value);
	final JSONString opString = (JSONString)obj.get("op");
	final Operation operation = Operation.get(opString.stringValue());
	final IInput left  = this.parseInput(obj.get("left"));
	final IInput right = this.parseInput(obj.get("right"));
	return new Gate(left, right, operation);
    }
}
