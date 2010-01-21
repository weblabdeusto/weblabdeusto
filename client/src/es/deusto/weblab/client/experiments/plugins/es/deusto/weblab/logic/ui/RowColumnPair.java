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

package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.ui;

import java.util.Arrays;
import java.util.List;
import java.util.Vector;

import com.google.gwt.core.client.GWT;

class RowColumnPair {
    private final int row;
    private final int column;
    
    private static int [] ROWS    = {0, 1, 2, 3, 4};
    private static int [] COLUMNS = {0, 2, 4 };

    private static List<RowColumnPair> BLANKS = Arrays.asList(new RowColumnPair[]{
	new RowColumnPair(0, 4),
	new RowColumnPair(4, 4),
    });
    
    public static RowColumnPair [] getRowsColumnPairs(){
	final List<RowColumnPair> pairs = new Vector<RowColumnPair>();
	for(int row : ROWS)
	    for(int column : COLUMNS)
		pairs.add(new RowColumnPair(row, column));
	
	return pairs.toArray(new RowColumnPair[]{});
    }
    
    private RowColumnPair(int row, int column){
	this.row = row;
	this.column = column;
    }
    
    public String getURL(){
	if(BLANKS.contains(this))
	    return GWT.getModuleBaseURL() + "img/logic/BLANK.png";
	
	return GWT.getModuleBaseURL() + "img/logic/F" + this.row + "C" + this.column + ".png";
    }

    public int getRow() {
	return this.row;
    }
    
    public int getColumn() {
	return this.column;
    }
    
    @Override
    public boolean equals(Object o){
	if(!(o instanceof RowColumnPair))
	    return false;
	final RowColumnPair other = (RowColumnPair)o;
	return this.row == other.row && this.column == other.column;
    }
    
    @Override
    public int hashCode(){
	return ("R" + this.row + "C" + this.column).hashCode();
    }
}
