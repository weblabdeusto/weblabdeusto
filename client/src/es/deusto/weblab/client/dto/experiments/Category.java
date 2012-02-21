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
package es.deusto.weblab.client.dto.experiments;

public class Category {
	private String category;
	
	public Category(){}
	
	public Category(String category){
		this.category = category;
	}

	public String getCategory() {
		return this.category;
	}

	public void setCategory(String category) {
		this.category = category;
	}

	@Override
	public String toString(){
		return "<category>"
				+ this.category
			 + "</category>"; 
	}
	
	@Override
	public boolean equals(Object other) {
		if ( other instanceof Category ) {
			return this.category.equals(((Category)other).category);	
		} else {
			return false;
		}
		
	}
}
