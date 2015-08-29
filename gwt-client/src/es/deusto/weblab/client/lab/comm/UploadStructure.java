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
package es.deusto.weblab.client.lab.comm;

import com.google.gwt.user.client.ui.FileUpload;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HasAlignment;
import com.google.gwt.user.client.ui.HasHorizontalAlignment;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Widget;

/**
 * Encapsulates the form used for selecting and uploading a file,
 * and is able to handle the uploading itself through a GWT
 * FileUpload object.
 */
public class UploadStructure extends Widget implements HasAlignment{
	
	private VerticalPanel panel;
	private final FormPanel     formPanel;
	private final FileUpload    fileUploader;
	private String fileInfo = "";
	
	public UploadStructure(){
		this.formPanel = new FormPanel();
		this.fileUploader = new FileUpload();		
		this.configurePanel();
		this.setWidth("100%");
		
		this.setElement(this.panel.getElement());
	}
	
	private void configurePanel() {
		this.panel = new VerticalPanel();
		this.panel.setHorizontalAlignment(HasHorizontalAlignment.ALIGN_CENTER);
		this.formPanel.setWidget(this.panel);
		this.panel.add(this.fileUploader);
	}
	
	public FormPanel getFormPanel(){
		return this.formPanel;
	}
	
	public FileUpload getFileUpload(){
		return this.fileUploader;
	}
	
	public void addInformation(Hidden information){
		this.panel.add(information);
	}
	
	public void removeInformation(Hidden information){
		this.panel.remove(information);
	}

	@Override
	public HorizontalAlignmentConstant getHorizontalAlignment() {
		return this.panel.getHorizontalAlignment();
	}

	@Override
	public void setHorizontalAlignment(HorizontalAlignmentConstant align) {
		this.panel.setHorizontalAlignment(align);
	}

	@Override
	public VerticalAlignmentConstant getVerticalAlignment() {
		return this.panel.getVerticalAlignment();
	}

	@Override
	public void setVerticalAlignment(VerticalAlignmentConstant align) {
		this.panel.setVerticalAlignment(align);
	}
	
	@Override
	public void setWidth(String width){
		this.panel.setWidth(width);
		this.formPanel.setWidth(width);
	}

	public void setFileInfo(String fileInfo) {
	    this.fileInfo = fileInfo;
	}

	public String getFileInfo() {
	    return this.fileInfo;
	}
}
