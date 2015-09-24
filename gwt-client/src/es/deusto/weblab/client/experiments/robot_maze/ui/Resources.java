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

package es.deusto.weblab.client.experiments.robot_maze.ui;

import com.google.gwt.resources.client.ClientBundle;
import com.google.gwt.resources.client.ImageResource;

interface Resources extends ClientBundle {
	
	@Source("res/up.png")
	ImageResource up();

	@Source("res/down.png")
	ImageResource down();

	@Source("res/left.png")
	ImageResource left();

	@Source("res/right.png")
	ImageResource right();

}
