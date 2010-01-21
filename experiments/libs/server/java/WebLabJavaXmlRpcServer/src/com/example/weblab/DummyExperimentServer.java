package com.example.weblab;

import java.io.File;

import es.deusto.weblab.experimentservers.IExperimentServer;
import es.deusto.weblab.experimentservers.WebLabException;

public class DummyExperimentServer implements IExperimentServer {
	
	public String sendCommand(String command)  throws WebLabException {
		System.out.println("I'm at send_command: " + command);
		return "ok";
	}

	public String sendFile(File file, String fileInfo)  throws WebLabException {
		System.out.println("I'm at send_program: " + file.getAbsolutePath() + "; fileInfo: " + fileInfo);
		return "ok";
	}
	
	public void dispose() {
		System.out.println("I'm at dispose");
	}

	public void startExperiment() throws WebLabException {
		System.out.println("I'm at startExperiment");
	}
}
