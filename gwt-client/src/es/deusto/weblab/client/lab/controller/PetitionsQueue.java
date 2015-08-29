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
package es.deusto.weblab.client.lab.controller;

import java.util.List;
import java.util.Vector;

import es.deusto.weblab.client.lab.controller.petitions.CommandPetition;
import es.deusto.weblab.client.lab.controller.petitions.GuiImagePetition;
import es.deusto.weblab.client.lab.controller.petitions.PollPetition;
import es.deusto.weblab.client.lab.controller.petitions.TimePetition;
import es.deusto.weblab.client.lab.controller.petitions.WebcamImagePetition;

/**
 * HTTP supports only two concurrent connections to the server
 * as specified in:
 * {@link http://tools.ietf.org/html/rfc2616#section-8.1.4}
 * 
 * We had some problems in WebLab-Deusto 2.0 with the Opera Mobile, 
 * since it used to enqueue all the petitions requested by the WebLab,
 * so if an image was requested, and then another image, and then a 
 * command was requested, the web browser would not send the command 
 * until the two images were served. In a few seconds, a lot of images
 * would block the queue and by the time the command was sent, the 
 * server had closed that session. 
 * 
 * In order to avoid this type of problems, WebLab-Deusto handles its
 * own queue, filtering the requests. If an image has been requested and
 * has not been served yet, any request of that image will be ignored, for
 * example. Any poll request will also be ignored if a command is being 
 * requested, and so on. Here is that implementation in GWT Java.
 * 
 * Rules:
 * 
 * <ul>
 * <li>Poll: only one at a time</li>
 * <li>Poll: only if there is no Command</li>
 * <li>Webcam Image: only one at a time</li>
 * <li>Order from most important to least important: Poll > Gui Image  > Command > Time > Webcam Image</li>
 * </ul>
 * 
 */
public class PetitionsQueue {
	
	private final List<CommandPetition> commands = new Vector<CommandPetition>();
	private final List<GuiImagePetition> guiImages = new Vector<GuiImagePetition>();
	private WebcamImagePetition webcamImagePetition = null;
	private PollPetition pollPetition = null;
	private TimePetition timePetition = null;
	
	/**
	 * Pushes a petition to the PetitionsQueue. When the {@link pop} method
	 * is called, it will be requested in the correct order. 
	 * 
	 * @param petition to be pushed
	 */
	public void push(PetitionNode petition){
		if(petition instanceof WebcamImagePetition)
			this.webcamImagePetition = (WebcamImagePetition)petition;
		else if(petition instanceof PollPetition){
			if(this.commands.size() == 0)
				this.pollPetition = (PollPetition)petition;
		}else if(petition instanceof TimePetition)
			this.timePetition = (TimePetition)petition;
		else if(petition instanceof CommandPetition){
			this.pollPetition = null;
			this.commands.add((CommandPetition)petition);
		}else if(petition instanceof GuiImagePetition)
			this.guiImages.add((GuiImagePetition)petition);
		else
			throw new IllegalStateException("Illegal state at PetitionsQueue::push: petition is not an instance of any of the above petitions"); 
	}

	/**
	 * Pops the next petition node that should be requested. 
	 * 
	 * @return the next PetitionNode, or null if no petition node was found
	 */
	public PetitionNode pop(){
		PetitionNode result;
		if(this.pollPetition != null){
			result = this.pollPetition;
			this.pollPetition = null;
			return result;
		}else if(this.guiImages.size() > 0){
			result = this.guiImages.remove(0);
			return result;
		}else if(this.commands.size() > 0){
			result = this.commands.remove(0);
			return result;
		}else if(this.timePetition != null){
			result = this.timePetition;
			this.timePetition = null;
			return result;
		}else if(this.webcamImagePetition != null){
			result = this.webcamImagePetition;
			this.webcamImagePetition = null;
			return result; 
		}
		return null;
	}
}
