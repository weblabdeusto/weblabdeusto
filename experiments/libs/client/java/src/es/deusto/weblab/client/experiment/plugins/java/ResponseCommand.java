package es.deusto.weblab.client.experiment.plugins.java;

public class ResponseCommand extends Command {

	private String commandString;
	
	ResponseCommand(String commandString){
		this.commandString = commandString;
	}
	
	public String getCommandString() {
		return this.commandString;
	}

}
