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

import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

public abstract class WlWidgetWithPressable extends VerticalPanel implements IWlWidget, IWlPressable{
	
	private Image currentImage;
	private Image oldImage;
	private final VerticalPanel visiblePanel;
	private final WlActionListenerContainer actionListenerContainer;
	
	private final Label title = new Label("");
	
	public WlWidgetWithPressable(){
		this.visiblePanel = new VerticalPanel();
		this.visiblePanel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.visiblePanel.setWidth("100%");
		this.actionListenerContainer = new WlActionListenerContainer();
		
		this.setWidth("100%");
		this.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);		
		this.visiblePanel.add(this.title);
		this.setStyleName("wl-pressable");
		
		this.add(this.visiblePanel);
	}
	
	/**
	 * Retrieves the title of the switch. The title is empty by default
	 * and may be set through the setTitle method.
	 */
	@Override
	public String getTitle() {
		return this.title.getText();
	}
	
	/**
	 * If set, shows a label containing the specified text. The title
	 * may be used to identify the widget.
	 */
	@Override
	public void setTitle(String title) {
		this.title.setVisible(true);
		this.title.setText(title);
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
	
	@Override
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
		return this;
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
		this.visiblePanel.add(this.title);
		this.visiblePanel.add(this.currentImage);
	}

	protected Image getOldImage() {
		return this.oldImage;
	}

	protected void setOldImage(Image oldImage) {
		this.oldImage = oldImage;
	} 
}
