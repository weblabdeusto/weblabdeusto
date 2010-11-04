package es.deusto.weblab.experimentservers;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;

import org.apache.ws.commons.util.Base64;
import org.apache.ws.commons.util.Base64.DecodingException;


public final class ExperimentServerXMLRPC {
	
	static class IExperimentServerHolder{
		private static IExperimentServer implementor;
		
		static void initialize(IExperimentServer implementor){
			IExperimentServerHolder.implementor = implementor;
		}
	}
	
	private IExperimentServer implementor;
	
	public ExperimentServerXMLRPC(){
		this.implementor = IExperimentServerHolder.implementor;
		if(this.implementor == null)
			throw new RuntimeException("Couldn't load " + ExperimentServerXMLRPC.class.getName() + ": implementor not found"); //Improve this
	}
	
	public final String test_me(String message){
		return message;
	}
	
	public final String send_file_to_device(String fileEncodedWithBase64, String fileInfo) throws WebLabException{
		System.out.println(fileEncodedWithBase64);
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
		return this.implementor.sendCommand(command);
	}
	
	public final String start_experiment() throws WebLabException{
		this.implementor.startExperiment();
		return "ok";
	}
	
	public final String dispose(){
		this.implementor.dispose();
		return "ok";
	}
}
