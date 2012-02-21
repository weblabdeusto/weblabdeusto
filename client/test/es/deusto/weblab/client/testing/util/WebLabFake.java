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
package es.deusto.weblab.client.testing.util;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

public class WebLabFake {
	
	private final Map<String, Object> nextReturn = new HashMap<String, Object>();
	private final Map<String, List<Methods>> methodsCalled = new HashMap<String, List<Methods>>();
	private int number = 0;
	private final List<Methods> methods = new Vector<Methods>();
	
	public class Methods{
		private int num;
		private Object [] parameters;
		
		public Methods(int n, Object [] p){
			this.num = n;
			this.parameters = p;
		}

		public int getNumber() {
			return this.num;
		}

		public void setNumber(int number) {
			this.num = number;
		}

		public Object[] getParameters() {
			return this.parameters;
		}

		public void setParameters(Object[] parameters) {
			this.parameters = parameters;
		}
	}
	
	protected void append(String methodName, Object [] parameters){
		if(!this.methodsCalled.containsKey(methodName)){
			this.methodsCalled.put(methodName, new Vector<Methods>());
		}
		
		//Add to methodsCalled
		final Methods m = new Methods(this.number, parameters);
		this.methodsCalled.get(methodName).add(m);
		
		//Add to methods
		this.methods.add(m);
		
		this.number++;
	}
	
	protected void append(String methodName){
		this.append(methodName, new Object[]{});
	}
	
	protected Object retrieveReturn(String methodName){
		if(!this.nextReturn.containsKey(methodName))
			throw new IllegalArgumentException("Illegal methodName (not set): " + methodName);
		return this.nextReturn.get(methodName);
	}

	public void appendReturn(String methodName, Object returnValue){
		this.nextReturn.put(methodName, returnValue);
	}
	
	public Methods getMethod(int n){
		return this.methods.get(n);
	}
	
	public int getMethodLength(){
		return this.methods.size();
	}
	
	public List<Methods> getMethodByName(String name){
		final List<Methods> v = this.methodsCalled.get(name);
		if(v == null)
			return new Vector<Methods>();
		return v;
	}
}
