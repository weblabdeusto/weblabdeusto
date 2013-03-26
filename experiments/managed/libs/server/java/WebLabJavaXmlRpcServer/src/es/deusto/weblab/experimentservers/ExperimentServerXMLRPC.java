package es.deusto.weblab.experimentservers;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import org.apache.ws.commons.util.Base64;
import org.apache.ws.commons.util.Base64.DecodingException;

import es.deusto.weblab.experimentservers.exceptions.ExperimentServerInternalException;
import es.deusto.weblab.experimentservers.exceptions.InvalidContentException;
import es.deusto.weblab.experimentservers.exceptions.WebLabException;


public final class ExperimentServerXMLRPC {
	
	private static String API_VERSION = "2";
	
	static class IExperimentServerHolder{
		private static volatile IExperimentServer implementor;
		
		static void initialize(IExperimentServer implementor){
			IExperimentServerHolder.implementor = implementor;
		}
	}
	
	private final IExperimentServer implementor;
	
	public ExperimentServerXMLRPC(){
		this.implementor = IExperimentServerHolder.implementor;
		if(this.implementor == null)
			throw new RuntimeException("Couldn't load " + ExperimentServerXMLRPC.class.getName() + ": implementor not found"); //Improve this
	}
	
	public final String test_me(String message){
		return message;
	}
	
	public final String get_api(){
		return API_VERSION;
	}
	
	public final boolean is_up_and_running() {
		return this.implementor.isUpAndRunning();
	}
	
	public final int should_finish() {
		return this.implementor.shouldFinish();
	}
	
	public final String start_experiment(String clientInitialData, String serverInitialData) throws WebLabException{
		if(this.implementor.isDebugging())
			System.out.println("Starting experiment...");
		return this.implementor.startExperiment(clientInitialData, serverInitialData);
	}
	
	public final String send_file_to_device(String fileEncodedWithBase64, String fileInfo) throws WebLabException{
		if(this.implementor.isDebugging())
			System.out.println("File sent:\n" + fileEncodedWithBase64);
		byte [] buffer;
		try {
			buffer = Base64.decode(fileEncodedWithBase64);
		} catch (DecodingException e) {
			throw new InvalidContentException("Invalid base64-encoded file");
		}
		
		File outputFile;
		try {
			outputFile = File.createTempFile("experiment_server_file_", ".dat");
			FileOutputStream fos = new FileOutputStream(outputFile);
			fos.write(buffer);
			fos.flush();
			fos.close();
		} catch (IOException e) {
			throw new ExperimentServerInternalException("Writing content to file: " + e.getMessage());
		}
		
		return this.implementor.sendFile(outputFile, fileInfo);
	}
	
	public final String send_command_to_device(String command) throws WebLabException{
		if(this.implementor.isDebugging())
			System.out.println("Command sent: " + command);
		return this.implementor.sendCommand(command);
	}
	
	public final String dispose(){
		if(this.implementor.isDebugging())
			System.out.println("Disposing");
		return this.implementor.dispose();
	}
}
