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

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.CircuitParser;
import es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.logic.circuit.InvalidCircuitException;

public class CircuitParserTestCase extends GWTTestCase {
    public void testParse() throws Exception{
	final CircuitParser circuitParser = new CircuitParser();
	final String response = "{\"op\": \"nor\", \"right\": {\"op\": \"or\", \"right\": {\"op\": \"or\", \"right\": false, \"left\": false}, \"left\": {\"op\": \"nand\", \"right\": false, \"left\": false}}, \"left\": {\"op\": \"or\", \"right\": {\"op\": \"nand\", \"right\": false, \"left\": false}, \"left\": {\"op\": \"and\", \"right\": false, \"left\": false}}}";
	circuitParser.parseCircuit(response);
    }
    
    public void testParseFail() throws Exception{
	final CircuitParser circuitParser = new CircuitParser();
	try{
	    circuitParser.parseCircuit("foo");
	    fail(InvalidCircuitException.class.getName() + " expected");
	}catch(InvalidCircuitException invalidCircuit){
	    // expected
	}
    }
    
    @Override
    public String getModuleName() {
	return "es.deusto.weblab.WebLabClient";
    }
}
