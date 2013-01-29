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
* Author: Pablo Orduña <pablo@ordunya.com>
*         Luis Rodriguez <luis.rodriguez@opendeusto.es>
*
*/ 
package es.deusto.weblab.client.lab.comm;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.Hidden;

import es.deusto.weblab.client.WebLabClient;
import es.deusto.weblab.client.comm.ICommonSerializer;
import es.deusto.weblab.client.comm.CommonCommunication;
import es.deusto.weblab.client.comm.WebLabRequestCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.SerializationException;
import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.comm.exceptions.WebLabServerException;
import es.deusto.weblab.client.comm.exceptions.core.SessionNotFoundException;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;


public class LabCommunication extends CommonCommunication implements ILabCommunication {

	public static final String FILE_SENT_ATTR  = "file_sent";
	public static final String SESSION_ID_ATTR = "session_id";
	public static final String FILE_INFO_ATTR  = "file_info"; 
	public static final String FILE_IS_ASYNC_ATTR = "is_async";
	
	public static final String WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY = "weblab.service.fileupload.post.url";
	public static final String DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL = "/weblab/web/upload/"; 
	
	
	// TODO: 
	// The existence of multiple managers is probably not required.
	// As of now, I don't think there can be two different active sessions at the
	// same time. 
	private final Map<SessionID, AsyncRequestsManager> asyncRequestsManagers =
		new HashMap<SessionID, AsyncRequestsManager>();
	
	public LabCommunication(IConfigurationManager configurationManager){
		super(configurationManager);
	}
	
	private String getFilePostUrl(){
		final String baseLocation = this.configurationManager.getProperty(WebLabClient.BASE_LOCATION, WebLabClient.DEFAULT_BASE_LOCATION);
		return baseLocation + this.configurationManager.getProperty(
					LabCommunication.WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY, 
					LabCommunication.DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL
				);
	}
	
	private class ReservationRequestCallback extends WebLabRequestCallback{
		private final IReservationCallback reservationCallback;
		
		public ReservationRequestCallback(IReservationCallback reservationCallback){
			super(reservationCallback);
			this.reservationCallback = reservationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ReservationStatus reservation;
			try {
				reservation = ((ILabSerializer)LabCommunication.this.serializer).parseGetReservationStatusResponse(response);
			} catch (final SerializationException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
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
			requestSerialized = ((ILabSerializer)this.serializer).serializeGetReservationStatusRequest(sessionId);
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
	
	private class ListExperimentsRequestCallback extends WebLabRequestCallback{
		private final IExperimentsAllowedCallback experimentsAllowedCallback;
		
		public ListExperimentsRequestCallback(IExperimentsAllowedCallback experimentsAllowedCallback){
			super(experimentsAllowedCallback);
			this.experimentsAllowedCallback = experimentsAllowedCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response){
			ExperimentAllowed [] experimentsAllowed;
			try {
				experimentsAllowed = ((ILabSerializer)LabCommunication.this.serializer).parseListExperimentsResponse(response);
			} catch (final SerializationException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.experimentsAllowedCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
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
			requestSerialized = ((ILabSerializer)this.serializer).serializeListExperimentsRequest(sessionId);
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

	private class PollRequestCallback extends WebLabRequestCallback{
		private final IVoidCallback voidCallback;
		
		public PollRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				((ILabSerializer)LabCommunication.this.serializer).parsePollResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
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
			requestSerialized = ((ILabSerializer)this.serializer).serializePollRequest(sessionId);
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

	private class ReserveExperimentRequestCallback extends WebLabRequestCallback{
		private final IReservationCallback reservationCallback;
		
		public ReserveExperimentRequestCallback(IReservationCallback reservationCallback){
			super(reservationCallback);
			this.reservationCallback = reservationCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ReservationStatus reservation;
			try {
				reservation = ((ILabSerializer)LabCommunication.this.serializer).parseReserveExperimentResponse(response);
			} catch (final SerializationException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final UnknownExperimentIdException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.reservationCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
				this.reservationCallback.onFailure(e);
				return;
			}
			this.reservationCallback.onSuccess(reservation);
		}
	}

	@Override
	public void reserveExperiment(SessionID sessionId, ExperimentID experimentId, JSONValue clientInitialData, IReservationCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((ILabSerializer)this.serializer).serializeReserveExperimentRequest(sessionId, experimentId, clientInitialData);
		} catch (final SerializationException e1) {
			callback.onFailure(e1);
			return;
		}
		final Map<String, String> headers = new HashMap<String, String>();
		headers.put("weblabdeusto-client", WebLabClient.IS_MOBILE?"weblabdeusto-web-mobile":"weblabdeusto-web-desktop");
        if(WebLabClient.getLocale() != null)
    		headers.put("weblabdeusto-locale", WebLabClient.getLocale());
		this.performRequest(
				requestSerialized, 
				callback, 
				new ReserveExperimentRequestCallback(callback),
				headers
			);
	}
	

	/**
	 * Callback to be notified when a send_command request finishes, either
	 * successfully or not.
	 */
	private class SendCommandRequestCallback extends WebLabRequestCallback{
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
				command = ((ILabSerializer)LabCommunication.this.serializer).parseSendCommandResponse(response);
			} catch (final SerializationException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			}
			this.responseCommandCallback.onSuccess(command);
		}
	}
	
	
	
	/**
	 * Internal callback which will be used for receiving and handling the response
	 * of a send_async_command request.
	 * TODO: Consider whether error checking is necessary here.
	 */
	private class SendAsyncCommandRequestCallback extends WebLabRequestCallback{
		private final IResponseCommandCallback responseCommandCallback;
		
		public SendAsyncCommandRequestCallback(IResponseCommandCallback responseCommandCallback){
			super(responseCommandCallback);
			this.responseCommandCallback = responseCommandCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			ResponseCommand command;
			try {
				command = ((ILabSerializer)LabCommunication.this.serializer).parseSendAsyncCommandResponse(response);
			} catch (final SerializationException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.responseCommandCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
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
			requestSerialized = ((ILabSerializer)this.serializer).serializeSendAsyncCommandRequest(sessionId, command);
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
					LabCommunication.this.asyncRequestsManagers.get(sessionId);

				// TODO: Consider some better way of handling the managers.
				if(asyncReqMngr == null)
					asyncReqMngr = new AsyncRequestsManager(LabCommunication.this, sessionId, (ILabSerializer) LabCommunication.this.serializer);
				
				asyncReqMngr.registerAsyncRequest(requestID, commandCallback);
			}

			@Override
			public void onFailure(CommException e) {
				commandCallback.onFailure(e);
			}
		};
		
		// Execute the initial request which will return the identifier and
		// register the command for polling.
		LabCommunication.this.performRequest(
				requestSerialized, 
				asyncCommandResponseCallback, 
				new SendAsyncCommandRequestCallback(asyncCommandResponseCallback)
			);
	}

	/**
	 * Sends a file asynchronously. Upon doing the async request to the server, it will be internally stored
	 * in the async requests manager, and polling will be done until the response is available. Then, the
	 * specified callback will be notified with the result.
	 */
	@Override
	public void sendAsyncFile(final SessionID sessionId, final UploadStructure uploadStructure,
			final IResponseCommandCallback callback) {
		// "Serialize" sessionId
    	
		// We will now create the Hidden elements which we will use to pass
		// the required POST parameters to the web script that will actually handle
		// the file upload request.
		
		final Hidden sessionIdElement = new Hidden();
		sessionIdElement.setName(LabCommunication.SESSION_ID_ATTR);
		sessionIdElement.setValue(sessionId.getRealId());
		
		final Hidden fileInfoElement = new Hidden();
		fileInfoElement.setName(LabCommunication.FILE_INFO_ATTR);
		fileInfoElement.setValue(uploadStructure.getFileInfo());
		
		final Hidden isAsyncElement = new Hidden();
		isAsyncElement.setName(LabCommunication.FILE_IS_ASYNC_ATTR);
		isAsyncElement.setValue("true");
		
		
		// Set up uploadStructure
		uploadStructure.addInformation(sessionIdElement);
		uploadStructure.addInformation(fileInfoElement);
		uploadStructure.addInformation(isAsyncElement);
		uploadStructure.getFileUpload().setName(LabCommunication.FILE_SENT_ATTR);
		uploadStructure.getFormPanel().setAction(this.getFilePostUrl());
		uploadStructure.getFormPanel().setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadStructure.getFormPanel().setMethod(FormPanel.METHOD_POST);

		// Register handler
		uploadStructure.getFormPanel().addSubmitCompleteHandler(new SubmitCompleteHandler() {

		    @Override
			public void onSubmitComplete(SubmitCompleteEvent event) {
		    	uploadStructure.removeInformation(sessionIdElement);

				final String resultMessage = event.getResults(); 
				// resultMessage will be a string such as SUCCESS@34KJ2341KJ

				if(GWT.isScript() && resultMessage == null) {
			    this.reportFail(callback);
				} else {
				    this.processResultMessage(callback, resultMessage);
				}
		    }

		    private void processResultMessage(IResponseCommandCallback commandCallback, String resultMessage) {
				final ResponseCommand parsedRequestIdCommand;
				try {
					// TODO: This should be improved.
					if(!resultMessage.toLowerCase().startsWith("success@"))
						throw new SerializationException("Async send file response does not start with success@");
					final String reslt = resultMessage.substring("success@".length());
					System.out.println("[DBG]: AsyncSendFile returned: " + reslt);
					parsedRequestIdCommand = new ResponseCommand(reslt);
				} catch (final SerializationException e) {
				    commandCallback.onFailure(e);
				    return; 
				}
//				} catch (final SessionNotFoundException e) {
//				    commandCallback.onFailure(e);
//				    return;
//				} catch (final WlServerException e) {
//				    commandCallback.onFailure(e);
//				    return;
//				}
			
				// We now have the request id of our asynchronous send_file request.
				// We will need to register the request with the asynchronous manager
				// so that it automatically polls and notifies us when the request finishes.
				final String requestID = parsedRequestIdCommand.getCommandString();
				
				AsyncRequestsManager asyncReqMngr = 
					LabCommunication.this.asyncRequestsManagers.get(sessionId);

				// TODO: Consider some better way of handling the managers.
				if(asyncReqMngr == null)
					asyncReqMngr = new AsyncRequestsManager(LabCommunication.this, sessionId, (ILabSerializer) LabCommunication.this.serializer);
				
				asyncReqMngr.registerAsyncRequest(requestID, commandCallback);
		    }
		    
		    private void reportFail(final IResponseCommandCallback callback) {
				GWT.log("reportFail could not async send the file", null);
				callback.onFailure(new CommException("Couldn't async send the file"));
		    }			
		});
	    
		// Submit
		uploadStructure.getFormPanel().submit();
	}

	@Override
	public void sendCommand(SessionID sessionId, Command command, IResponseCommandCallback callback) {
		String requestSerialized;
		try {
			requestSerialized = ((ILabSerializer)this.serializer).serializeSendCommandRequest(sessionId, command);
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
	
	private class FinishedRequestCallback extends WebLabRequestCallback{
		private final IVoidCallback voidCallback;
		
		public FinishedRequestCallback(IVoidCallback voidCallback){
			super(voidCallback);
			this.voidCallback = voidCallback;
		}
		
		@Override
		public void onSuccessResponseReceived(String response) {
			try {
				((ILabSerializer)LabCommunication.this.serializer).parseFinishedExperimentResponse(response);
			} catch (final SerializationException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final SessionNotFoundException e) {
				this.voidCallback.onFailure(e);
				return;
			} catch (final WebLabServerException e) {
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
			requestSerialized = ((ILabSerializer)this.serializer).serializeFinishedExperimentRequest(sessionId);
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

	/**
	 * Sends the file specified through the upload structure to the server. This is done through an
	 * HTTP post, which is received by a server-side web-script that actually does call the server-side
	 * send_file method.
	 */
	@Override
	public void sendFile(SessionID sessionId, final UploadStructure uploadStructure, final IResponseCommandCallback callback) {
		// "Serialize" sessionId
	    	
		// We will now create the Hidden elements which we will use to pass
		// the required POST parameters to the web script that will actually handle
		// the file upload request.
		
		final Hidden sessionIdElement = new Hidden();
		sessionIdElement.setName(LabCommunication.SESSION_ID_ATTR);
		sessionIdElement.setValue(sessionId.getRealId());
		

		final Hidden fileInfoElement = new Hidden();
		fileInfoElement.setName(LabCommunication.FILE_INFO_ATTR);
		fileInfoElement.setValue(uploadStructure.getFileInfo());
		
// 		TODO: This could be enabled. Left disabled for now just in case it has
//		side effects. It isn't really required because the is_async attribute is
//		optional and false by default.
		final Hidden isAsyncElement = new Hidden();
		isAsyncElement.setName(LabCommunication.FILE_IS_ASYNC_ATTR);
		isAsyncElement.setValue("false");
		
		// Set up uploadStructure
		uploadStructure.addInformation(sessionIdElement);
		uploadStructure.addInformation(fileInfoElement);
		uploadStructure.addInformation(isAsyncElement);
		uploadStructure.getFileUpload().setName(LabCommunication.FILE_SENT_ATTR);
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
			    parsedResponseCommand = ((ILabSerializer)LabCommunication.this.serializer).parseSendFileResponse(resultMessage);
			} catch (final SerializationException e) {
			    callback.onFailure(e);
			    return;
			} catch (final SessionNotFoundException e) {
			    callback.onFailure(e);
			    return;
			} catch (final WebLabServerException e) {
			    callback.onFailure(e);
			    return;
			}
			callback.onSuccess(parsedResponseCommand);
		    }
		    private void reportFail(final IResponseCommandCallback callback) {
			GWT.log("reportFail could not send the file", null);
			callback.onFailure(new CommException("Couldn't send the file"));
		    }			
		});
	    
		// Submit
		uploadStructure.getFormPanel().submit();
	}

	@Override
	// For testing purposes
	protected ICommonSerializer createSerializer(){
		return new LabSerializerJSON();
	}


}
