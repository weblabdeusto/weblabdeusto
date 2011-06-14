/*
* Copyright (C) 2005-2009 University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo@ordunya.com>
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.comm;

import java.util.Map;

import com.google.gwt.core.client.GWT;
import java.util.HashMap;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.comm.WlCommonCommunication;
import es.deusto.weblab.client.comm.WlRequestCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.WlServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.AsyncRequestStatus;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCheckAsyncCommandStatusCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;


public class WlLabCommunication extends WlCommonCommunication implements IWlLabCommunication {

	public static final String FILE_SENT_ATTR  = "file_sent";
	public static final String SESSION_ID_ATTR = "session_id";
	public static final String FILE_INFO_ATTR  = "file_info"; 
	
	public static final String WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY = "weblab.service.fileupload.post.url";
	public static final String DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL = "/weblab/web/upload/"; 
	
	
	// TODO: 
	// The existence of multiple managers is probably not required
	// As of now, I don't think there can be two different active sessions at the
	// same time. 
	private final Map<SessionID, AsyncRequestsManager> asyncRequestsManagers =
		new HashMap<SessionID, AsyncRequestsManager>();
	
	public WlLabCommunication(IConfigurationManager configurationManager){
		super(configurationManager);
	}
	
	private String getFilePostUrl(){
		return this.configurationManager.getProperty(
					WlLabCommunication.WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY, 
					WlLabCommunication.DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL
				);
	}
	
	private class ReservationRequestCallback extends WlRequestCallback{
		private final IReservationCallback reservationCallback;
		
		public ReservationRequestCallback(IReservationCallback reservationCallback){
			super(reservationCallback);
			this.reservationCallback = reservationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ReservationStatus reservation;
			try {
				reservation = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseGetReservationStatusResponse(response);
			} catch (final SerializationException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.reservationCallback.onFailure(e);
				return;
			}
			this.reservationCallback.onSuccess(reservation);
		}
	}
	
	@Override
	public void getReservationStatus(SessionID sessionId, IReservationCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializeGetReservationStatusRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new ReservationRequestCallback(callback)
			);
	}
	
	private class ListExperimentsRequestCallback extends WlRequestCallback{
		private final IExperimentsAllowedCallback experimentsAllowedCallback;
		
		public ListExperimentsRequestCallback(IExperimentsAllowedCallback experimentsAllowedCallback){
			super(experimentsAllowedCallback);
			this.experimentsAllowedCallback = experimentsAllowedCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ExperimentAllowed [] experimentsAllowed;
			try {
				experimentsAllowed = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseListExperimentsResponse(response);
			} catch (final SerializationException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			}
			this.experimentsAllowedCallback.onSuccess(experimentsAllowed);
		}
	}

	@Override
	public void listExperiments(SessionID sessionId, IExperimentsAllowedCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializeListExperimentsRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new ListExperimentsRequestCallback(callback)
			);
	}

	private class PollRequestCallback extends WlRequestCallback{
		private final IVoidCallback voidCallback;
		
		public PollRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				((IWlLabSerializer)WlLabCommunication.this.serializer).parsePollResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.voidCallback.onFailure(e);
				return;
			}
			this.voidCallback.onSuccess();
		}
	}

	@Override
	public void poll(SessionID sessionId, IVoidCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializePollRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new PollRequestCallback(callback)
			);
	}

	private class ReserveExperimentRequestCallback extends WlRequestCallback{
		private final IReservationCallback reservationCallback;
		
		public ReserveExperimentRequestCallback(IReservationCallback reservationCallback){
			super(reservationCallback);
			this.reservationCallback = reservationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ReservationStatus reservation;
			try {
				reservation = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseReserveExperimentResponse(response);
			} catch (final SerializationException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final UnknownExperimentIdException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.reservationCallback.onFailure(e);
				return;
			}
			this.reservationCallback.onSuccess(reservation);
		}
	}

	@Override
	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, IReservationCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializeReserveExperimentRequest(sessionId, experimentId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new ReserveExperimentRequestCallback(callback)
			);
	}
	

	/**
	 * Callback to be notified when a send_command request finishes, either
	 * successfully or not.
	 */
	private class SendCommandRequestCallback extends WlRequestCallback{
		private final IResponseCommandCallback responseCommandCallback;
		
		/**
		 * Constructs the SendCommandRequestCallback.
		 * @param responseCommandCallback Callback to be invoked whenever a request
		 * fails or succeeds. IResponseCommandCallback extends IWlAsyncCallback, and
		 * together they have two separate methods to handle both cases. 
		 */
		public SendCommandRequestCallback(IResponseCommandCallback responseCommandCallback){
			super(responseCommandCallback);
			this.responseCommandCallback = responseCommandCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ResponseCommand command;
			try {
				command = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseSendCommandResponse(response);
			} catch (final SerializationException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			}
			this.responseCommandCallback.onSuccess(command);
		}
	}
	
	
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
	private class CheckAsyncCommandStatusRequestCallback extends WlRequestCallback{
		private final IResponseCheckAsyncCommandStatusCallback responseCheckAsyncCommandStatusCallback;
		
		/**
		 * Constructs the CheckAsyncCommandStatusRequestCallback.
		 * @param responseCommandCallback Callback to be invoked whenever a request
		 * fails or succeeds. IResponseCommandCallback extends IWlAsyncCallback, and
		 * together they have two separate methods to handle both cases. 
		 */
		public CheckAsyncCommandStatusRequestCallback(IResponseCheckAsyncCommandStatusCallback responseCheckAsyncCommandStatusCallback){
			super(responseCheckAsyncCommandStatusCallback);
			this.responseCheckAsyncCommandStatusCallback = responseCheckAsyncCommandStatusCallback;
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
				asyncRequests = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseCheckAsyncCommandStatusResponse(response);
			} catch (final SerializationException e) {
				this.responseCheckAsyncCommandStatusCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.responseCheckAsyncCommandStatusCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
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
	 * callbacks of the response.
	 */
	private class AsyncRequestsManager {
		
		// Map relating the request identifiers, to the callbacks to invoke
		// when the associated requests finish. Async request are commands, 
		// so IResponseCommandCallbacks are appropriate.
		private Map<String, IResponseCommandCallback> requests = 
			new HashMap<String, IResponseCommandCallback>();
		
		private Timer timer;
		
		private SessionID sessionId;
		
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
					cmdCallback.onFailure(new WlCommException("Async cmd reported failure: " + response));
			
				// TODO: There might be some other exception type more appropriate 
				// than the above.
			}
		}
		
		/**
		 * Creates an AsyncRequestManager.
		 * @param sessionId Session identifier whose asynchronous commands to handle
		 */
		public AsyncRequestsManager(SessionID sessionId) {
			
			this.sessionId = sessionId;
			
			this.timer = new Timer() {
				@Override
				public void run() {
					
					// Build a request to check the state of every ongoing
					// command.
					final String [] requestIds = new String[AsyncRequestsManager.this.requests.size()];
					AsyncRequestsManager.this.requests.keySet().toArray(requestIds);
					
					String requestSerialized = null;
					final IWlLabSerializer serializer = (IWlLabSerializer)WlLabCommunication.this.serializer;
					try {
						requestSerialized = serializer.serializeCheckAsyncCommandStatusRequest(AsyncRequestsManager.this.sessionId, 
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
						public void onFailure(WlCommException e) {
							// TODO: Handle this error.
						}

						@Override
						public void onSuccess(AsyncRequestStatus [] requests) {
							// Update the status of every request included in the
							// response. If the status did not change it will be
							// a NO-OP anyway.
							for(AsyncRequestStatus r : requests)
								AsyncRequestsManager.this.updateStatus(r);
						}
					};
					
					// Create the callback that will initially receive and parse the
					// raw results, passing the higher-level callback (defined above) 
					// to it, which will receive a high-level desearialized object with 
					// the results.
					final CheckAsyncCommandStatusRequestCallback rawRequestCallback = 
						new CheckAsyncCommandStatusRequestCallback(checkStatusCallback); 

					// Send the request and prepare to be notified.
					performRequest(
							requestSerialized, 
							checkStatusCallback, 
							rawRequestCallback
						);
						
				} //! run
			}; //! new Timer
		
			
			// TODO: The timer should somehow only run when/if there are actually
			// pending commands. For now, it will run forever.
			this.timer.scheduleRepeating(2000);
		}
		
		public void registerAsyncRequest(String requestIdentifier, 
				IResponseCommandCallback responseCommandCallback) {
			this.requests.put(requestIdentifier, responseCommandCallback);
		}
		
	} //! class AsyncRequestsManager
	
	
	/**
	 * Internal callback which will be used for receiving and handling the response
	 * of a send_async_command request.
	 * TODO: Consider whether error checking is necessary here.
	 */
	private class SendAsyncCommandRequestCallback extends WlRequestCallback{
		private final IResponseCommandCallback responseCommandCallback;
		
		public SendAsyncCommandRequestCallback(IResponseCommandCallback responseCommandCallback){
			super(responseCommandCallback);
			this.responseCommandCallback = responseCommandCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ResponseCommand command;
			try {
				command = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseSendCommandResponse(response);
			} catch (final SerializationException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			}
			this.responseCommandCallback.onSuccess(command);
		}
	}
	
	
	/**
	 * Sends a command to be executed asynchronously on the server-side. 
	 * 
	 * @param command The command
	 * @param callback Callback which will be notified when the asynchronous execution
	 * ends and the response of the server is retrieved. This response may take a 
	 * particularly long time to arrive. 
	 */
	@Override
	public void sendAsyncCommand(final SessionID sessionId, Command command,
			final IResponseCommandCallback commandCallback) {
		
		// Serialize the request as an asynchronous send command request.
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializeSendAsyncCommandRequest(sessionId, command);
		} catch (final SerializationException e1) {
			commandCallback.onFailure(e1);
			return;
		}
		
		// Declare the callback that will be called once the initial response of the asynchronous request
		// is received. Because the asynchronous request is precisely not executed synchronously, this response
		// is simply a request id, through which we will later poll to check the actual status and result of
		// the request.
		final IResponseCommandCallback asyncCommandResponseCallback = new IResponseCommandCallback() {
			@Override
			public void onSuccess(ResponseCommand responseCommand) {
				final String requestID = responseCommand.getCommandString();
				
				// We will now need to register the command in the local manager, so
				// that it handles the polling.
				AsyncRequestsManager asyncReqMngr = 
					WlLabCommunication.this.asyncRequestsManagers.get(sessionId);

				// TODO: Consider some better way of handling the managers.
				if(asyncReqMngr == null)
					asyncReqMngr = new AsyncRequestsManager(sessionId);
				
				asyncReqMngr.registerAsyncRequest(requestID, commandCallback);
			}

			@Override
			public void onFailure(WlCommException e) {
				commandCallback.onFailure(e);
			}
		};
		
		// Execute the initial request which will return the identifier and
		// register the command for polling.
		this.performRequest(
				requestSerialized, 
				asyncCommandResponseCallback, 
				new SendAsyncCommandRequestCallback(asyncCommandResponseCallback)
			);
	}

	@Override
	public void sendAsyncFile(SessionID sessionId, final UploadStructure uploadStructure,
			IResponseCommandCallback callback) {
		// "Serialize" sessionId
    	
//		final Hidden sessionIdElement = new Hidden();
//		sessionIdElement.setName(WlLabCommunication.SESSION_ID_ATTR);
//		sessionIdElement.setValue(sessionId.getRealId());
//		
//		final Hidden fileInfoElement = new Hidden();
//		fileInfoElement.setName(WlLabCommunication.FILE_INFO_ATTR);
//		fileInfoElement.setValue(uploadStructure.getFileInfo());
//		
//		// Set up uploadStructure
//		uploadStructure.addInformation(sessionIdElement);
//		uploadStructure.addInformation(fileInfoElement);
//		uploadStructure.getFileUpload().setName(WlLabCommunication.FILE_SENT_ATTR);
//		uploadStructure.getFormPanel().setAction(this.getFilePostUrl());
//		uploadStructure.getFormPanel().setEncoding(FormPanel.ENCODING_MULTIPART);
//		uploadStructure.getFormPanel().setMethod(FormPanel.METHOD_POST);
//
//		// Register handler
//		uploadStructure.getFormPanel().addSubmitCompleteHandler(new SubmitCompleteHandler() {
//
//		    @Override
//			public void onSubmitComplete(SubmitCompleteEvent event) {
//			uploadStructure.removeInformation(sessionIdElement);
//
//			final String resultMessage = event.getResults();
//			if(GWT.isScript() && resultMessage == null) {
//			    this.reportFail(callback);
//			} else {
//			    this.processResultMessage(callback, resultMessage);
//			}
//		    }
//
//		    private void processResultMessage(IResponseCommandCallback callback, String resultMessage) {
//			final ResponseCommand parsedResponseCommand;
//			try {
//			    parsedResponseCommand = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseSendFileResponse(resultMessage);
//			} catch (final SerializationException e) {
//			    callback.onFailure(e);
//			    return;
//			} catch (final SessionNotFoundException e) {
//			    callback.onFailure(e);
//			    return;
//			} catch (final WlServerException e) {
//			    callback.onFailure(e);
//			    return;
//			}
//			callback.onSuccess(parsedResponseCommand);
//		    }
//		    private void reportFail(final IResponseCommandCallback callback) {
//			GWT.log("reportFail could not send the file", null);
//			callback.onFailure(new WlCommException("Couldn't send the file"));
//		    }			
//		});
//	    
//		// Submit
//		uploadStructure.getFormPanel().submit();
	}

	@Override
	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializeSendCommandRequest(sessionId, command);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new SendCommandRequestCallback(callback)
			);
	}
	
	private class FinishedRequestCallback extends WlRequestCallback{
		private final IVoidCallback voidCallback;
		
		public FinishedRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				((IWlLabSerializer)WlLabCommunication.this.serializer).parseFinishedExperimentResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WlServerException e) {
				this.voidCallback.onFailure(e);
				return;
			}
			this.voidCallback.onSuccess();
		}
	}

	@Override
	public void finishedExperiment(SessionID sessionId, IVoidCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((IWlLabSerializer)this.serializer).serializeFinishedExperimentRequest(sessionId);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		this.performRequest(
				requestSerialized, 
				callback, 
				new FinishedRequestCallback(callback)
			);
	}

	@Override
	public void sendFile(SessionID sessionId, final UploadStructure uploadStructure, final IResponseCommandCallback callback) {
		// "Serialize" sessionId
	    	
		final Hidden sessionIdElement = new Hidden();
		sessionIdElement.setName(WlLabCommunication.SESSION_ID_ATTR);
		sessionIdElement.setValue(sessionId.getRealId());
		
		final Hidden fileInfoElement = new Hidden();
		fileInfoElement.setName(WlLabCommunication.FILE_INFO_ATTR);
		fileInfoElement.setValue(uploadStructure.getFileInfo());
		
		// Set up uploadStructure
		uploadStructure.addInformation(sessionIdElement);
		uploadStructure.addInformation(fileInfoElement);
		uploadStructure.getFileUpload().setName(WlLabCommunication.FILE_SENT_ATTR);
		uploadStructure.getFormPanel().setAction(this.getFilePostUrl());
		uploadStructure.getFormPanel().setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadStructure.getFormPanel().setMethod(FormPanel.METHOD_POST);

		// Register handler
		uploadStructure.getFormPanel().addSubmitCompleteHandler(new SubmitCompleteHandler() {

		    @Override
			public void onSubmitComplete(SubmitCompleteEvent event) {
			uploadStructure.removeInformation(sessionIdElement);

			final String resultMessage = event.getResults();
			if(GWT.isScript() && resultMessage == null) {
			    this.reportFail(callback);
			} else {
			    this.processResultMessage(callback, resultMessage);
			}
		    }

		    private void processResultMessage(IResponseCommandCallback callback, String resultMessage) {
			final ResponseCommand parsedResponseCommand;
			try {
			    parsedResponseCommand = ((IWlLabSerializer)WlLabCommunication.this.serializer).parseSendFileResponse(resultMessage);
			} catch (final SerializationException e) {
			    callback.onFailure(e);
			    return;
			} catch (final SessionNotFoundException e) {
			    callback.onFailure(e);
			    return;
			} catch (final WlServerException e) {
			    callback.onFailure(e);
			    return;
			}
			callback.onSuccess(parsedResponseCommand);
		    }
		    private void reportFail(final IResponseCommandCallback callback) {
			GWT.log("reportFail could not send the file", null);
			callback.onFailure(new WlCommException("Couldn't send the file"));
		    }			
		});
	    
		// Submit
		uploadStructure.getFormPanel().submit();
	}

	@Override
	// For testing purposes
	protected IWlCommonSerializer createSerializer(){
		return new WlLabSerializerJSON();
	}


}
