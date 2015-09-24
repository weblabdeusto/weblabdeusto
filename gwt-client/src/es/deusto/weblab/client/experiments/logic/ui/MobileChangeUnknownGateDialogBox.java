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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

/**
 * 
 */
package es.deusto.weblab.client.experiments.logic.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;

import es.deusto.weblab.client.experiments.logic.circuit.Operation;
import es.deusto.weblab.client.i18n.IWebLabI18N;

class MobileChangeUnknownGateDialogBox extends DialogBox {
    
	static IWebLabI18N i18n = GWT.create(IWebLabI18N.class);
	private final Map<Image, Operation> images2operations = new HashMap<Image, Operation>();
	
    public MobileChangeUnknownGateDialogBox(final MobileLogicExperiment board) {
      this.setText(i18n.chooseCorrectGate());

      final ClickHandler imageHandler = new ClickHandler() {
	        @Override
			public void onClick(ClickEvent event) {
	  	  MobileChangeUnknownGateDialogBox.this.hide();
	  	  
	  	  final Operation operation = MobileChangeUnknownGateDialogBox.this.images2operations.get(event.getSource());
	  	  board.changeUnknownGate(operation);
	     }
	  };
      
      final VerticalPanel figures = new VerticalPanel();
      
      for(final Operation operation : Operation.getOperations()){
		  final Image image = new Image(board.getURL(operation));
		  this.images2operations.put(image, operation);
		  image.addClickHandler(imageHandler);
		  image.addStyleName(LogicExperiment.Style.LOGIC_MOUSE_POINTER_HAND);
		  figures.add(image);
      }
      
      this.setWidget(figures);	  
    }
  }