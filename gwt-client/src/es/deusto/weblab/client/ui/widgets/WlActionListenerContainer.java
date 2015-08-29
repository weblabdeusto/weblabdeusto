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
package es.deusto.weblab.client.ui.widgets;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class WlActionListenerContainer {
	private final List<IWlActionListener> actionListeners;
	
	public WlActionListenerContainer(){
		this.actionListeners = new ArrayList<IWlActionListener>();
	}
	
	public void addActionListener(IWlActionListener listener){
		this.actionListeners.add(listener);
	}
	
	public void removeActionListener(IWlActionListener listener){
		this.actionListeners.remove(listener);
	}

	public void fireActionListeners(IWlWidget sender){
		final Iterator<IWlActionListener> it = this.actionListeners.iterator();
		while(it.hasNext()){
			final IWlActionListener listener = it.next();
			listener.onAction(sender);
		}
	}
}
