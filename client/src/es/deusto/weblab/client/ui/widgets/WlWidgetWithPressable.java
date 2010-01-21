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
package es.deusto.weblab.client.ui.widgets;

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public abstract class WlWidgetWithPressable implements IWlWidget, IWlPressable{
	
	private Image currentImage;
	private Image oldImage;
	private final VerticalPanel visiblePanel;
	private final WlActionListenerContainer actionListenerContainer;
	
	public WlWidgetWithPressable(){
		this.visiblePanel = new VerticalPanel();
		this.visiblePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.actionListenerContainer = new WlActionListenerContainer();
	}
	
	public void addActionListener(IWlActionListener listener){
		this.actionListenerContainer.addActionListener(listener);
	}
	
	public void removeActionListener(IWlActionListener listener){
		this.actionListenerContainer.removeActionListener(listener);
	}
	
	protected void fireActionListeners(){
		this.actionListenerContainer.fireActionListeners(this);
	}
	
	public void press(){
		this.changeState(this.currentImage,this.oldImage);
		this.toggleCurrent();
	}
	
	protected void changeState(Image original, Image newOne){
		for(int i = 0; i < this.visiblePanel.getWidgetCount(); ++i)
			if(this.visiblePanel.getWidget(i) == original){
				this.visiblePanel.remove(i);
				this.visiblePanel.add(newOne);
				break;
			}
	}

	private void toggleCurrent() {
		final Image tmp = this.currentImage;
		this.currentImage = this.oldImage;
		this.oldImage = tmp;
	}
	
	@Override
	public Widget getWidget(){
		return this.visiblePanel;
	}

	protected Image getCurrentImage() {
		return this.currentImage;
	}

	protected void setCurrentImage(Image currentImage) {
		this.currentImage = currentImage;
	}
	
	protected void setCurrentVisibleImage(Image currentImage){
		this.currentImage = currentImage;
		for(int i = 0; i < this.visiblePanel.getWidgetCount(); ++i)
			this.visiblePanel.remove(i);
		this.visiblePanel.add(this.currentImage);
	}

	protected Image getOldImage() {
		return this.oldImage;
	}

	protected void setOldImage(Image oldImage) {
		this.oldImage = oldImage;
	}
}
