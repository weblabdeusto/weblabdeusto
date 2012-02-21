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
* Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/

package es.deusto.weblab.client.dto.experiments;

/**
 * Represents the status of an asynchronous request. An asynchronous request
 * can be either a send_async_command or send_async_file. They are
 * asynchronously executed on the server-side, on their own threads.
 * They are uniquely identified through a request-id. 
 */
public class AsyncRequestStatus {
	
	private boolean requestRunning;
	private boolean requestFinishedSuccessfully;
	private String response;
	private String requestID;
	
	/**
	 * Creates an object to describe the status of an asynchronous request.
	 * @param requestID Unique identifier string for the request.
	 * @param requestRunning True if the request has not finished yet. False otherwise.
	 * @param requestFinishedSuccessfully True if the request finished without errors. 
	 * False if it finished with an error, or if the request has not yet finished.
	 * @param response The response, which can either be a success or error response. Will only be available
	 * if the request has finished (is no longer running).
	 */
	public AsyncRequestStatus(String requestID, boolean requestRunning, 
			boolean requestFinishedSuccessfully, String response) {
		this.requestID = requestID;
		this.requestRunning = requestRunning;
		this.requestFinishedSuccessfully = requestFinishedSuccessfully;
		this.response = response;
		
		// A request cannot be both running and successfully finished.
		if(this.requestRunning && this.requestFinishedSuccessfully)
			throw new RuntimeException("Trying to construct an AsyncRequestStatus object with an invalid state");
	}
	
	/** 
	 * @return Unique ID string of the request.
	 */
	public String getRequestID() {
		return this.requestID;
	}
	
	/**
	 * @return String containing the response to the request, if it did finish.
	 * It can either be a success or error response.
	 * @see isRunning
	 * @see isSuccessfullyFinished
	 */
	public String getResponse() {
		return this.response;
	}
	
	/**
	 * @return True if the request is still running (and hence not finished), false
	 * otherwise.
	 */
	public boolean isRunning() {
		return this.requestRunning;
	}
	
	/**
	 * @return True if the request has finished and it has done so successfully,
	 * false otherwise.
	 */
	public boolean isSuccessfullyFinished() {
		return this.requestFinishedSuccessfully;
	}
	
	/**
	 * @return True if the request has finished but an error occurred. 
	 */
	public boolean isError() {
		return (!this.requestRunning && !this.requestFinishedSuccessfully );
	}
}
