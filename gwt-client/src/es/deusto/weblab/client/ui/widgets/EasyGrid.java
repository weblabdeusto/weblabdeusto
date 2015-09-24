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
* Author: Luis Rodriguez <luis.rodriguez@gmail.com>
*
*/

package es.deusto.weblab.client.ui.widgets;

import java.util.ArrayList;

import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Widget;


/**
 * EasyGrid is meant to provide the same features as a Grid, from which it inherits,
 * but it is meant to be used from UIBinder. Hence, the number of rows and columns can be 
 * set through its rows and cols properties (rather than through the ctor), and the 
 * default add() method is supported, so that its widgets can be specified from XML and
 * setWidget() is no longer required. Widgets are arranged in the table in order (as they
 * appear in the XML), from left to right and from top to bottom.
 */
public class EasyGrid extends Grid {
	
	/**
	 * List that will store every widget added to the grid.
	 */
	private final ArrayList<Widget> widgets = new ArrayList<Widget>();
	private int cols = -1;
	private int rows = -1;
	
	/**
	 * Creates or resizes the table. Cols and Rows need to have been set already. Every
	 * internally stored widget is assigned a cell in order, from left to right and top to bottom.
	 */
	private void createTable()
	{
		this.resize(this.rows, this.cols);
		
		int widgetsSet = 0;
		for(int j = 0; j < this.rows && widgetsSet < this.widgets.size(); j++)
			for(int i = 0; i < this.cols && widgetsSet < this.widgets.size(); i++, widgetsSet++)
				this.setWidget(j, i, this.widgets.get(widgetsSet));
	}

	/**
	 * Constructs an EasyGrid.
	 */
	public EasyGrid() {
		this.resize(4, 4);
	}
	
	/**
	 * Sets the number of columns of the table.
	 * @param cols Number of columns.
	 */
	public void setCols(int cols) {
		this.cols = cols;
		if(this.rows != -1 && cols != -1)
			this.createTable();
	}
	
	/**
	 * Sets the number of rows of the table.
	 * @param rows Number of rows.
	 */
	public void setRows(int rows) {
		this.rows = rows;
		if(rows != -1 && this.cols != -1)
			this.createTable();
	}
	
	/**
	 * Adds a widget to the table. The EasyGrid stores widgets internally without
	 * actually displaying them, until both the cols and rows numbers have been
	 * set.
	 */
	@Override
	public void add(Widget widget)
	{
		this.widgets.add(widget);
	}

}
