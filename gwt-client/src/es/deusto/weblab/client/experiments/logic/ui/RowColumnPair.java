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

package es.deusto.weblab.client.experiments.logic.ui;

import java.util.Arrays;
import java.util.List;
import java.util.Vector;

import com.google.gwt.resources.client.ImageResource;

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
		for(final int row : RowColumnPair.ROWS)
			for(final int column : RowColumnPair.COLUMNS)
				pairs.add(new RowColumnPair(row, column));

		return pairs.toArray(new RowColumnPair[]{});
	}

	private RowColumnPair(int row, int column){
		this.row = row;
		this.column = column;
	}

	public ImageResource getImageResourceWeb(Resources res){
		if(RowColumnPair.BLANKS.contains(this))
			return res.bigBLANK();
		
		switch(this.row){
			case 0:
				switch(this.column){
					case 0: return res.bigF0C0();
					case 2: return res.bigF0C2();
				}
				break;

			case 1:
				switch(this.column){
					case 0: return res.bigF1C0();
					case 2: return res.bigF1C2();
					case 4: return res.bigF1C4();
				}
				break;
				
			case 2:
				switch(this.column){
					case 0: return res.bigF2C0();
					case 2: return res.bigF2C2();
					case 4: return res.bigF2C4();
				}
				break;
				
			case 3:
				switch(this.column){
					case 0: return res.bigF3C0();
					case 2: return res.bigF3C2();
					case 4: return res.bigF3C4();
				}
				break;
				
			case 4:
				switch(this.column){
					case 0: return res.bigF4C0();
					case 2: return res.bigF4C2();
				}
				break;
		}
		
		throw new RuntimeException("Invalid ColumnPair: row=" + this.row + "; column=" + this.column);
	}

	public ImageResource getImageResourceMobile(MobileResources res){
		if(RowColumnPair.BLANKS.contains(this))
			return res.smallBLANK();
		
		switch(this.row){
			case 0:
				switch(this.column){
					case 0: return res.smallF0C0();
					case 2: return res.smallF0C2();
				}
				break;

			case 1:
				switch(this.column){
					case 0: return res.smallF1C0();
					case 2: return res.smallF1C2();
					case 4: return res.smallF1C4();
				}
				break;
				
			case 2:
				switch(this.column){
					case 0: return res.smallF2C0();
					case 2: return res.smallF2C2();
					case 4: return res.smallF2C4();
				}
				break;
				
			case 3:
				switch(this.column){
					case 0: return res.smallF3C0();
					case 2: return res.smallF3C2();
					case 4: return res.smallF3C4();
				}
				break;
				
			case 4:
				switch(this.column){
					case 0: return res.smallF4C0();
					case 2: return res.smallF4C2();
				}
				break;
		}
		
		throw new RuntimeException("Invalid ColumnPair: row=" + this.row + "; column=" + this.column);
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
