package es.deusto.weblab.client.experiment.plugins.java;

import java.util.Hashtable;
import java.util.Map;

import netscape.javascript.JSObject;

public class BoardController {
	private final JSObject jsobject;
	private final Map sentCommands = new Hashtable();
	private int counter = 0;
	
	BoardController(JSObject jsobject){
		this.jsobject = jsobject;
	}

	public void sendCommand(String command, ICommandCallback callback){
		final int commandId = this.addCommandCallback(callback);
		this.jsobject.call("wl_sendCommand", new Object[]{command, new Integer(commandId) });
	}
	
	public void sendCommand(Command command, ICommandCallback callback){
		final int commandId = this.addCommandCallback(callback);
		this.jsobject.call("wl_sendCommand", new Object[]{command.getCommandString(), new Integer(commandId) });
	}
	
	private int addCommandCallback(ICommandCallback callback){
		final int commandId;
		synchronized (this) {
			commandId = ++this.counter;
			this.sentCommands.put(new Integer(commandId), callback);
		}
		return commandId;
	}
	
	void handleCommandResponse(String message, int commandId){
		final ICommandCallback callback;
		synchronized(this){
			callback = (ICommandCallback)this.sentCommands.remove(new Integer(commandId));
		}
		callback.onSuccess(new ResponseCommand(message));
	}
	
	void handleCommandError(String message, int commandId){
		final ICommandCallback callback;
		synchronized(this){
			callback = (ICommandCallback)this.sentCommands.remove(new Integer(commandId));
		}
		callback.onFailure(message);
	}
	
	public void onClean(){
		this.jsobject.call("wl_onClean", new Object[]{});
	}
}
