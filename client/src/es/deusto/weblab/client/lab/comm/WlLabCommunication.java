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
*
*/ 
package es.deusto.weblab.client.lab.comm;

import com.google.gwt.core.client.GWT;
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
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ExperimentID;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.ReservationStatus;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.comm.exceptions.UnknownExperimentIdException;


public class WlLabCommunication extends WlCommonCommunication implements IWlLabCommunication {

	public static final String FILE_SENT_ATTR  = "file_sent";
	public static final String SESSION_ID_ATTR = "session_id";
	public static final String FILE_INFO_ATTR  = "file_info"; 
	
	public static final String WEBLAB_FILE_UPLOAD_POST_SERVICE_URL_PROPERTY = "weblab.service.fileupload.post.url";
	public static final String DEFAULT_WEBLAB_FILE_UPLOAD_POST_SERVICE_URL = "/weblab/fileUpload.py"; 
	
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

	private class SendCommandRequestCallback extends WlRequestCallback{
		private final IResponseCommandCallback responseCommandCallback;
		
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
