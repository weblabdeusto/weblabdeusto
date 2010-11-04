package es.deusto.weblab.client.experiment.plugins.java;

import javax.swing.JApplet;

import netscape.javascript.JSObject;

public abstract class WebLabApplet extends JApplet {
	private static final long serialVersionUID = -7383940394030524725L;
	
	private JSObject jsobject;
	private ConfigurationManager configurationManager;
	private BoardController boardController; 
	
	public WebLabApplet(){
	}
	
	public void init(){
		this.jsobject = JSObject.getWindow(this);
		this.configurationManager = new ConfigurationManager(this.jsobject);
		this.boardController      = new BoardController(this.jsobject);
	}
	
	protected BoardController getBoardController(){
		return this.boardController;
	}
	
	protected ConfigurationManager getConfigurationManager(){
		return this.configurationManager;
	}
	
	public final void handleCommandResponse(String msg, int commandId){
		this.boardController.handleCommandResponse(msg, commandId);
	}

	public final void handleCommandError(String msg, int commandId){
		this.boardController.handleCommandError(msg, commandId);
	}

	// Methods that can be overridden
	
	public void setTime(int time) {}
	
	public void startInteraction() {}
	
	public void end() {}
}
