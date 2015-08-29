package es.deusto.weblab.client.lab.comm;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.user.client.Timer;

import es.deusto.weblab.client.comm.WebLabRequestCallback;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.AsyncRequestStatus;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCheckAsyncCommandStatusCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

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


	/**
	 * Callback to be notified when a check_async_command_status request finishes, 
	 * either successfully or not. The response will be a JSON string containing
	 * a map with the status of every single async command that we queried, so 
	 * we will have to parse and handle it appropriately. 
	 * 
	 * This callback will receive the raw response to the check query. That response will 
	 * then be deserialized into an array of AsyncRequestStatus objects, and forwarded
	 * to the provided IResponseCheckAsyncCommandStatusCallback, which will be the one to
	 * actually handle the response.
	 */
	class CheckAsyncCommandStatusRequestCallback extends WebLabRequestCallback {
		
		private final IResponseCheckAsyncCommandStatusCallback responseCheckAsyncCommandStatusCallback;
		
		private final ILabSerializer serializer;
		
		/**
		 * Constructs the CheckAsyncCommandStatusRequestCallback.
		 * @param responseCommandCallback Callback to be invoked whenever a request
		 * fails or succeeds. IResponseCommandCallback extends IWlAsyncCallback, and
		 * together they have two separate methods to handle both cases. 
		 * @param serializer Serializer which will be used to encode the requests.
		 */
		public CheckAsyncCommandStatusRequestCallback(IResponseCheckAsyncCommandStatusCallback responseCheckAsyncCommandStatusCallback,
				ILabSerializer serializer) {
			super(responseCheckAsyncCommandStatusCallback);
			this.responseCheckAsyncCommandStatusCallback = responseCheckAsyncCommandStatusCallback;
			this.serializer = serializer;
		}
		
		/**
		 * Method that will be invoked when the check_async_command_status response
		 * is available. 
		 * @param string The response, a JSON-encoded map of every async command state.
		 */
		@Override
		public void onSuccessResponseReceived(String response) {
			
			// The response is a string containing the status of the async requests
			// we are interested in, encoded in JSON. We will first use the serializer
			// to deserialize it into an array of AsyncRequestStatus, with each
			// AsyncRequestStatus containing the status, and possibly the response,
			// of one async command.
			final AsyncRequestStatus [] asyncRequests;
			
			try {
				asyncRequests = this.serializer.parseCheckAsyncCommandStatusResponse(response);
			} catch (final SessionNotFoundException e) {
				this.responseCheckAsyncCommandStatusCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
				this.responseCheckAsyncCommandStatusCallback.onFailure(e);
				return;
			} catch (SerializationException e) {
				this.responseCheckAsyncCommandStatusCallback.onFailure(e);
				return;
			} 
			
			this.responseCheckAsyncCommandStatusCallback.onSuccess(asyncRequests);
		}
	}




	/**
	 * Manages the asynchronous requests of a specific session.
	 * Does polling on pending requests periodically to check whether
	 * they have finished. If they have, it notifies the awaiting
	 * callbacks of the response to their command. This is internally done
	 * through a timer that runs periodically whenever there is work to be
	 * done.
	 */
	public class AsyncRequestsManager {
		
		// Map relating the request identifiers, to the callbacks to invoke
		// when the associated requests finish. Async request are commands, 
		// so IResponseCommandCallbacks are appropriate.
		private final Map<String, IResponseCommandCallback> requests = 
			new HashMap<String, IResponseCommandCallback>();
		
		private final LabCommunication comm;
		
		private final Timer timer;
		private boolean timerRunning = false;
		
		private final SessionID sessionId;
		
		private final ILabSerializer serializer;

		
		/**
		 * Creates an AsyncRequestManager.
		 * @param comm Reference to the WlLabCommunication object through which requests will be carried out
		 * @param sessionId Session identifier whose asynchronous commands to handle
		 * @param serializer Serializer which we will use to encode and decode
		 * the requests and responses
		 */
		public AsyncRequestsManager(final LabCommunication comm, SessionID sessionId, final ILabSerializer serializer) {
			
			this.comm = comm;
			
			this.sessionId = sessionId;
			
			this.serializer = serializer;
			
			this.timer = new Timer() {
				@Override
				public void run() {
					
					// Build a request to check the state of every ongoing
					// command.
					final String [] requestIds = new String[AsyncRequestsManager.this.requests.size()];
					AsyncRequestsManager.this.requests.keySet().toArray(requestIds);
					
					String requestSerialized = null;
					try {
						requestSerialized = AsyncRequestsManager.this.serializer.serializeCheckAsyncCommandStatusRequest(AsyncRequestsManager.this.sessionId, 
								requestIds);
					} catch (SerializationException e) {
						// TODO: Handle this exception properly. The request is not linked
						// to a particular command (but to several) so we cannot simply
						// invoke its callback.
					}
					
					// Define the callback that will be invoked when the check 
					// async command status request finishes. It is noteworthy that
					// the check_async_command_status request returns a map describing the
					// status of every single request whose identifier was specified.
					
					final IResponseCheckAsyncCommandStatusCallback checkStatusCallback = new IResponseCheckAsyncCommandStatusCallback() {
						@Override
						public void onFailure(CommException e) {
							// TODO: Handle this error.
						}

						@Override
						public void onSuccess(AsyncRequestStatus [] requests) {
							// Update the status of every request included in the
							// response. If the status did not change it will be
							// a NO-OP anyway.
							for(AsyncRequestStatus r : requests)
								AsyncRequestsManager.this.updateStatus(r);
							
							// If we have don't have anymore requests, we cancel the timer 
							if(AsyncRequestsManager.this.requests.isEmpty()) {
								AsyncRequestsManager.this.timer.cancel();
								AsyncRequestsManager.this.timerRunning = false;
								System.out.println("[AsyncRequestsManager] Timer disabled");
							}
						}
					};
					
					// Create the callback that will initially receive and parse the
					// raw results, passing the higher-level callback (defined above) 
					// to it, which will receive a high-level desearialized object with 
					// the results.
					final CheckAsyncCommandStatusRequestCallback rawRequestCallback = 
						new CheckAsyncCommandStatusRequestCallback(checkStatusCallback, AsyncRequestsManager.this.serializer); 

					// Send the request and prepare to be notified.
					AsyncRequestsManager.this.comm.performRequest(
							requestSerialized, 
							checkStatusCallback, 
							rawRequestCallback
						);
						
				} //! run
			}; //! new Timer
		
		}
		
		
		
		/**
		 * Provides an update for an async request. It will check whether
		 * the request finished. If so, it will remove it from its internal list
		 * and invoke its callback.
		 * @param request Status of a request
		 */
		public void updateStatus(AsyncRequestStatus request) {
			if(!request.isRunning()) {
				
				final IResponseCommandCallback cmdCallback = this.requests.get(request.getRequestID());
				this.requests.remove(request.getRequestID());
				
				final String response = request.getResponse();
				
				if(request.isSuccessfullyFinished())
					cmdCallback.onSuccess(new ResponseCommand(response));
				else
					cmdCallback.onFailure(new CommException("Async cmd reported failure: " + response));
			
				// TODO: There might be some other exception type more appropriate 
				// than the above.
			}
		}
		
		public void registerAsyncRequest(String requestIdentifier, 
				IResponseCommandCallback responseCommandCallback) {
			
			this.requests.put(requestIdentifier, responseCommandCallback);
			
			// If the timer isn't running already, we start it, so that
			// the request we have just added to the list gets handled.
			if(!this.timerRunning) {
				this.timer.scheduleRepeating(2000);
				this.timerRunning = true;
				System.out.println("[AsyncRequestsManager] Timer enabled");
			}
			
		}
		
	} //! class AsyncRequestsManager