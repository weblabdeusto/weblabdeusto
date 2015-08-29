/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.experiments.robot_maze.ui;

import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.user.client.Event;
import com.google.gwt.user.client.Event.NativePreviewEvent;
import com.google.gwt.user.client.Event.NativePreviewHandler;

import es.deusto.weblab.client.ui.widgets.IWlDisposableWidget;

class InternalNativePreviewHandler implements NativePreviewHandler, IWlDisposableWidget {
	
	private boolean active = false;
	private final ControlPanel controlPanel;
	
	InternalNativePreviewHandler(ControlPanel controlPanel) {
		this.controlPanel = controlPanel;
	}
	
	void activate() {
		this.active = true;
	}

	void deactivate() {
		this.active = false;
	}

	@Override
	public void dispose() {
		deactivate();
	}
	
	@Override
	public void onPreviewNativeEvent(NativePreviewEvent event) {
		if(!this.active)
			return;
	
		if(event.getTypeInt() == Event.ONKEYDOWN) {
			switch(event.getNativeEvent().getKeyCode()) {
				case KeyCodes.KEY_UP:
					this.controlPanel.onUpMouseDown(null);
					event.cancel();
					break;
				case KeyCodes.KEY_DOWN:
					this.controlPanel.onDownMouseDown(null);
					event.cancel();
					break;
				case KeyCodes.KEY_LEFT:
					this.controlPanel.onLeftMouseDown(null);
					event.cancel();
					break;
				case KeyCodes.KEY_RIGHT:
					this.controlPanel.onRightMouseDown(null);
					event.cancel();
					break;
			}
		} else if(event.getTypeInt() == Event.ONKEYUP) {
			switch(event.getNativeEvent().getKeyCode()) {
				case KeyCodes.KEY_UP:
					this.controlPanel.onUpMouseUp(null);
					event.cancel();
					break;
				case KeyCodes.KEY_DOWN:
					this.controlPanel.onDownMouseUp(null);
					event.cancel();
					break;
				case KeyCodes.KEY_LEFT:
					this.controlPanel.onLeftMouseUp(null);
					event.cancel();
					break;
				case KeyCodes.KEY_RIGHT:
					this.controlPanel.onRightMouseUp(null);
					event.cancel();
					break;
			}
		}
	}
}