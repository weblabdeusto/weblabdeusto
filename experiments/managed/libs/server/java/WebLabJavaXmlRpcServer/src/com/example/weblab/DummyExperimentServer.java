package com.example.weblab;

import java.io.File;

import es.deusto.weblab.experimentservers.ExperimentServer;
import es.deusto.weblab.experimentservers.exceptions.ExperimentServerInstantiationException;
import es.deusto.weblab.experimentservers.exceptions.WebLabException;

public class DummyExperimentServer extends ExperimentServer {

	public DummyExperimentServer() throws ExperimentServerInstantiationException {
		super();
	}

    // Typical server initial data:
    // [java] The server provided me this data: 
    //        {
    //          "request.locale": "es", 
    //          "request.experiment_id.experiment_name": "dummy", 
    //          "request.experiment_id.category_name": "Dummy experiments", 
    //          "priority.queue.slot.initialization_in_accounting": true, 
    //          "priority.queue.slot.start": "2013-03-27 00:36:08.397675", 
    //          "priority.queue.slot.length": "200", 
    //          "request.username": "admin" 
    //        }
	@Override
	public String startExperiment(String clientInitialData, String serverInitialData) throws WebLabException {
		System.out.println("I'm at startExperiment");
		System.out.println("The client provided me this data: " + clientInitialData);
		System.out.println("The server provided me this data: " + serverInitialData);
		return "{}";
	}

	@Override
	public String sendFile(File file, String fileInfo)  throws WebLabException {
		System.out.println("I'm at send_program: " + file.getAbsolutePath() + "; fileInfo: " + fileInfo);
		return "ok";
	}
	
	@Override
	public String sendCommand(String command)  throws WebLabException {
		System.out.println("I'm at send_command: " + command);
		return "ok";
	}
	
	@Override
	public String dispose() {
		System.out.println("I'm at dispose");
		return "ok";
	}
	
	@Override
	public boolean isUpAndRunning() {
		return false;
	}
}
