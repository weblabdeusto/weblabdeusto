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
* Author: Jaime Irurzun <jaime.irurzun@gmail.com>
*
*/

/**
 * 
 */
package es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.ui;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.VerticalPanel;

import es.deusto.weblab.client.experiments.plugins.es.deusto.weblab.logic.circuit.Operation;

class MobileChangeUnknownGateDialogBox extends DialogBox {
    
	private final Map<Image, Operation> images2operations = new HashMap<Image, Operation>();
	
    public MobileChangeUnknownGateDialogBox(final MobileWlDeustoLogicBasedBoard board) {
      setText("Choose the correct gate:");

      final ClickHandler imageHandler = new ClickHandler() {
	        public void onClick(ClickEvent event) {
	  	  MobileChangeUnknownGateDialogBox.this.hide();
	  	  
	  	  final Operation operation = MobileChangeUnknownGateDialogBox.this.images2operations.get(event.getSource());
	  	  board.changeUnknownGate(operation);
	     }
	  };
      
      final VerticalPanel figures = new VerticalPanel();
      
      for(Operation operation : Operation.getOperations()){
		  final Image image = new Image(board.getURL(operation));
		  this.images2operations.put(image, operation);
		  image.addClickHandler(imageHandler);
		  image.addStyleName(WlDeustoLogicBasedBoard.Style.LOGIC_MOUSE_POINTER_HAND);
		  figures.add(image);
      }
      
      setWidget(figures);	  
    }
  }