/*
* Copyright (C) 2012 onwards University of Deusto
* All rights reserved.
*
* This software is licensed as described in the file COPYING, which
* you should have received as part of this distribution.
*
* This software consists of contributions made by many individuals, 
* listed below:
*
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.lab.experiments;

import java.util.HashMap;
import java.util.Map;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONBoolean;
import com.google.gwt.json.client.JSONNull;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;
import com.google.gwt.user.client.ui.Hidden;

import es.deusto.weblab.client.comm.exceptions.CommException;
import es.deusto.weblab.client.configuration.ConfigurationRetriever;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.EmptyResponseCommand;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.lab.comm.FileResponseException;
import es.deusto.weblab.client.lab.comm.UploadStructure;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;

public class JSBoardBaseController implements IBoardBaseController {
	
	/*
	 * general metadata methods
	 */
	@Override
	public boolean isFacebook() {
		return isFacebookImpl();
	}

	@Override
	public void clean() {
		cleanImpl();
	}

	@Override
	public void finish() {
		finishImpl();
	}

	@Override
	public void stopPolling() {
		stopPollingImpl();
	}

	@Override
	public void disableFinishOnClose() {
		disableFinishOnCloseImpl();
	}

	/*
	 * INTERACTION METHODS
	 */
	
	@Override
	public void sendCommand(Command command) {
		sendCommandImpl(command.getCommandString(), NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}
	
	@Override
	public void sendCommand(Command command, IResponseCommandCallback callback) {
		sendCommandImpl(command.getCommandString(), new CallbackWrapper(callback));
	}
	
	@Override
	public void sendCommand(String command) {
		sendCommandImpl(command, NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendCommand(String command, IResponseCommandCallback callback) {
		sendCommandImpl(command, new CallbackWrapper(callback));
	}

	@Override
	public void sendAsyncCommand(Command command) {
		sendAsyncCommandImpl(command.getCommandString(), NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendAsyncCommand(Command command, IResponseCommandCallback callback) {
		sendAsyncCommandImpl(command.getCommandString(), new CallbackWrapper(callback));
	}

	@Override
	public void sendAsyncCommand(String command) {
		sendAsyncCommandImpl(command, NullSimpleResponseCallback.NULL_RESPONSE_CALLBACK);
	}

	@Override
	public void sendAsyncCommand(String command, IResponseCommandCallback callback) {
		sendAsyncCommandImpl(command, new CallbackWrapper(callback));
	}

	@Override
	public void sendFile(final UploadStructure uploadStructure, final IResponseCommandCallback callback) {
		final Hidden reservationIdElement = new Hidden("reservation_id", getReservationId());
		
		// Set up uploadStructure
		uploadStructure.addInformation(reservationIdElement);
		uploadStructure.addInformation(new Hidden("file_info", uploadStructure.getFileInfo()));
		uploadStructure.addInformation(new Hidden("is_async", "false"));
		uploadStructure.getFileUpload().setName("file_sent");
		uploadStructure.getFormPanel().setAction(getFileUploadUrl());
		uploadStructure.getFormPanel().setEncoding(FormPanel.ENCODING_MULTIPART);
		uploadStructure.getFormPanel().setMethod(FormPanel.METHOD_POST);

		// Register handler
		uploadStructure.getFormPanel().addSubmitCompleteHandler(new SubmitCompleteHandler() {

			@Override
			public void onSubmitComplete(SubmitCompleteEvent event) {
				uploadStructure.removeInformation(reservationIdElement);

				final String resultMessage = event.getResults();
				if(GWT.isScript() && resultMessage == null) {
					this.reportFail(callback);
				} else {
					this.processResultMessage(callback, resultMessage);
				}
			}

			private void processResultMessage(IResponseCommandCallback callback, String resultMessage) {				
				if(resultMessage == null) {
					if (GWT.isScript()) {
						callback.onSuccess(new EmptyResponseCommand());
					}
					return;
				}
				
				final ResponseCommand parsedResponseCommand;
				try {
					parsedResponseCommand = parseSendFileResponse(resultMessage);
				} catch (final FileResponseException e) {
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


	private ResponseCommand parseSendFileResponse(final String responseText) throws FileResponseException{
		final String startMessage = "<body>";
		final String endMessage = "</body>";
		
		final int startPoint = responseText.trim().toLowerCase().indexOf(startMessage) + startMessage.length();
		final int endPoint = responseText.trim().toLowerCase().lastIndexOf(endMessage);
		
		// Sometimes the browsers provide us directly the body of the message, sometimes it provides the full HTML message
		final String parsedResponse;
		if(startPoint < 0 || endPoint < 0 || startPoint > endPoint)
		    parsedResponse = responseText;
		else
		    parsedResponse = responseText.trim().substring(startPoint, endPoint);
		
		final int firstAT = parsedResponse.indexOf("@");
		if(firstAT < 0)
		    throw new FileResponseException("Sending file failed: response should have at least one '@' symbol");
		final String firstWord = parsedResponse.substring(0, firstAT);
		final String restOfText = parsedResponse.substring(firstAT + 1);
		
		if(firstWord.toLowerCase().equals("success")){
		    return new ResponseCommand(restOfText);
		}else if(firstWord.toLowerCase().equals("error")){
		    final int secondAT = restOfText.indexOf("@");
		    final String faultString = restOfText.substring(secondAT + 1);
		    throw new FileResponseException(faultString);
		}else
		    throw new FileResponseException("Sending file failed: first element must be 'success' or 'error'");
	}
	
	static native String getReservationId() /*-{
		return $wnd.weblab.getReservationId();
	}-*/;

	static native String getFileUploadUrl() /*-{
		return $wnd.weblab.getFileUploadUrl();
	}-*/;

	@Override
	public void sendAsyncFile(UploadStructure uploadStructure, IResponseCommandCallback callback) {
		// This is not implemented
		sendFile(uploadStructure, callback);
	}
	
	/*
	 * JSNI implementations
	 * 
	 */
	
	public static ConfigurationRetriever getExperimentConfiguration() {
		final Map<String, Object> rawConfig = new HashMap<String, Object>();
		populateConfiguration(rawConfig);
		log("Config loaded into map. Keys: " + rawConfig.keySet().size());
		final Map<String, JSONValue> config = new HashMap<String, JSONValue>();
		for (String key : rawConfig.keySet()) {
			final Object rawValue = rawConfig.get(key);
			final JSONValue value;
			if (rawValue == null) {
				value = JSONNull.getInstance();
			} else if (rawValue instanceof Number){
				value = new JSONNumber(((Number)rawValue).doubleValue());
			} else if (rawValue instanceof Boolean) {
				value = JSONBoolean.getInstance((Boolean)rawValue);
			} else if (rawValue instanceof String) {
				value = new JSONString((String)rawValue);
			} else {
				log("Invalid value for key: " + key + "; value: " + rawValue);
				try {
				    log("; original type: " + rawValue.getClass().getName());
				} catch(Exception ex) {

				}
				continue;
			}
			log("Key: " + key + "; value: " + value);
			config.put(key, value);
		}
		return new ConfigurationRetriever(config);
	}
	
	public static native void log(String message) /*-{
		if ($wnd.WEBLAB_DEBUG === true) { 
			$wnd.console.log("[gwt] " + message);
		}
	}-*/;
	
	static native void populateConfiguration(Map<String, Object> configObj) /*-{
		var configuration = $wnd.gwt_experiment_config.config;
		for (var key in configuration) {
			var value = configuration[key];

            // If we call ::put directly with a JS object as parameter, it gets passed as an encapsulated
            // JavaScriptObject, and is not automagically converted to the right type (Boolean, for instance).
            // That is why we check the type here, and explicitly instance the Java type.

			if(typeof(value) == "boolean") {
			    configObj.@java.util.Map::put(Ljava/lang/Object;Ljava/lang/Object;)(key, @java.lang.Boolean::valueOf(Z)(value));
			} else if(typeof(value) == "number") {
			    configObj.@java.util.Map::put(Ljava/lang/Object;Ljava/lang/Object;)(key, @java.lang.Double::valueOf(D)(value));
			}
            else
			    configObj.@java.util.Map::put(Ljava/lang/Object;Ljava/lang/Object;)(key, value);
		}
	}-*/;

    public static native void experimentLoaded() /*-{
        $wnd.experimentLoadedPromise.resolve();
    }-*/;

    public static native void experimentLoadedFailed(String message) /*-{
        $wnd.experimentLoadedPromise.reject({ error: message });
    }-*/;

	
	public static native String getClientCodeName() /*-{
		return $wnd.gwt_experiment_config.client_code_name;
	}-*/; 
	
	public static native boolean isMobile() /*-{
		return $wnd.gwt_experiment_config.mobile;
	}-*/;
	
	public static native String getBaseLocation() /*-{
		return $wnd.gwt_experiment_config.base_location;
	}-*/;

	static native boolean isFacebookImpl() /*-{
		return $wnd.gwt_experiment_config.facebook;
	}-*/;
	
	static native void cleanImpl() /*-{
		return $wnd.weblab.cleanExperiment();
	}-*/;

	static native void finishImpl() /*-{
		return $wnd.weblab.finishExperiment();
	}-*/;
	
	static native void stopPollingImpl() /*-{
		return $wnd.weblab.stopPolling();
	}-*/;

	static native void disableFinishOnCloseImpl() /*-{
		return $wnd.weblab.disableFinishOnClose();
	}-*/;
	
	static native void sendCommandImpl(String commandString, ISimpleResponseCallback callback) /*-{
		$wnd.weblab.sendCommand(commandString)
			.done(function(success) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onSuccess(Ljava/lang/String;)(success);
			})
			.fail(function(error) {
				callback.@es.deusto.weblab.client.lab.experiments.ISimpleResponseCallback::onFailure(Ljava/lang/String;)(error);
			});
	}-*/;

	static void sendAsyncCommandImpl(String commandString, ISimpleResponseCallback callback) {
		// This method is not implemented
		sendCommandImpl(commandString, callback);
	}
	
	public static void registerExperiment(ExperimentBase experiment) {
        boolean error = false;
        try {
            if (isStartReserved())
                experiment.initializeReserved();
            else
                experiment.initialize();
            
            registerExperimentImpl(experiment);
        } catch (RuntimeException e) {
            error = true;
            e.printStackTrace();
            experimentLoadedFailed(e.getMessage());
            throw e;
        }
        if (!error) {
            experimentLoaded();
        }
	}
	
	static native boolean isStartReserved() /*-{
		return $wnd.gwt_experiment_config.start_reserved;
	}-*/;
	
	static native void registerExperimentImpl(ExperimentBase experiment) /*-{
		$wnd.weblab.onStart(function (time, config) {
			experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::start(ILjava/lang/String;)(time, config);
		});
		
		$wnd.weblab.setOnGetInitialDataCallback(function () {
			return experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::getInitialData()();
		});
		
		$wnd.weblab.onSetTime(function (time) {
			experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::setTime(I)(time);
		});
		
		$wnd.weblab.onQueue(function () {
			experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::queued()();
		});
		
		$wnd.weblab.onFinish(function() {
			experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::end()();
		});
		
		// only if it expects postEnd we call onProcessResults(). onProcessResults internally assumes the expectsPostEnd (if called, then it expects it)
		if (experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::expectsPostEnd()()) {
			$wnd.weblab.onProcessResults(function(initialData, endData) {
				experiment.@es.deusto.weblab.client.lab.experiments.ExperimentBase::postEnd(Ljava/lang/String;Ljava/lang/String;)(initialData, endData);
			});
		}
	}-*/;
	
	public static native void show() /*-{
		$wnd.weblab.show();
	}-*/;
	
	public static native void onConfigurationLoaded(Runnable task) /*-{
		$wnd.weblab.onConfigLoad(function() {
			task.@java.lang.Runnable::run()();
		});
	}-*/; 
}
