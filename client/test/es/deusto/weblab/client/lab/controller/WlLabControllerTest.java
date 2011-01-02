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
package es.deusto.weblab.client.lab.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.comm.FakeWlCommonCommunication;
import es.deusto.weblab.client.comm.callbacks.ISessionIdCallback;
import es.deusto.weblab.client.comm.callbacks.IUserInformationCallback;
import es.deusto.weblab.client.comm.callbacks.IVoidCallback;
import es.deusto.weblab.client.comm.exceptions.WlCommException;
import es.deusto.weblab.client.comm.exceptions.login.LoginException;
import es.deusto.weblab.client.configuration.FakeConfiguration;
import es.deusto.weblab.client.configuration.IConfigurationManager;
import es.deusto.weblab.client.dto.SessionID;
import es.deusto.weblab.client.dto.experiments.Category;
import es.deusto.weblab.client.dto.experiments.Command;
import es.deusto.weblab.client.dto.experiments.Experiment;
import es.deusto.weblab.client.dto.experiments.ExperimentAllowed;
import es.deusto.weblab.client.dto.experiments.ResponseCommand;
import es.deusto.weblab.client.dto.reservations.CancellingReservationStatus;
import es.deusto.weblab.client.dto.reservations.ConfirmedReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingConfirmationReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingInstancesReservationStatus;
import es.deusto.weblab.client.dto.reservations.WaitingReservationStatus;
import es.deusto.weblab.client.dto.users.Role;
import es.deusto.weblab.client.dto.users.User;
import es.deusto.weblab.client.lab.comm.FakeWlLabCommunication;
import es.deusto.weblab.client.lab.comm.callbacks.IExperimentsAllowedCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IReservationCallback;
import es.deusto.weblab.client.lab.comm.callbacks.IResponseCommandCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactoryResetter;
import es.deusto.weblab.client.lab.ui.FakeUIManager;
import es.deusto.weblab.client.testing.util.WlFake.Methods;

public class WlLabControllerTest  extends GWTTestCase{
	
	private IConfigurationManager configurationManager;
	private FakeWlLabCommunication fakeCommunications;
	private FakeUIManager fakeUIManager;
	private FakePollingHandler fakePollingHandler;
	
	private static final int WAITING_INSTANCES_MIN_POLL_TIME = 12345;
	private static final int WAITING_INSTANCES_MAX_POLL_TIME = 123450;
	private static final int WAITING_MIN_POLL_TIME           = 12346;
	private static final int WAITING_MAX_POLL_TIME           = 123460;
	private static final int WAITING_CONFIRMATION_POLL_TIME  = 12347;
	
	@Override
	public void gwtSetUp(){
		ExperimentFactoryResetter.reset();
	}
	
	public void testLoginFailure() throws Exception{
		final WlLabController controller = this.createController();
		controller.login("whatever", "whatever");
		
		List<Methods> v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGIN);
		Assert.assertEquals(1, v.size());
		final Methods m = v.get(0);
		final Object [] parametersReceived = m.getParameters();
		Assert.assertEquals(3, parametersReceived.length);
		final ISessionIdCallback callback = (ISessionIdCallback)parametersReceived[2];
		
		callback.onFailure(new LoginException("WRONG!"));
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_WRONG_LOGIN_OR_PASSWORD_GIVEN);
		Assert.assertEquals(1, v.size());
		
		callback.onFailure(new WlCommException("other error"));
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_SESSION);
		Assert.assertEquals(1, v.size());
	}
	
	public void testLoginSucceeded() throws Exception{
		final User user = new User("porduna", "Pablo Orduña Fernández", "porduna@tecnologico.deusto.es", new Role("student"));

		final WlLabController controller = this.createController();
		
		// login
		controller.login("whatever", "whatever");
		List<Methods> v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGIN);
		Assert.assertEquals(1, v.size());
		Methods m = v.get(0);
		final Object [] parametersReceived = m.getParameters();
		Assert.assertEquals(3, parametersReceived.length);
		final ISessionIdCallback sessionIdCallback = (ISessionIdCallback)parametersReceived[2];
		final SessionID sessionID = new SessionID("your session!");

		sessionIdCallback.onSuccess(sessionID);
		v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.GET_USER_INFORMATION);
		Assert.assertEquals(1, v.size());		
		m = v.get(0);
		Assert.assertEquals(2, m.getParameters().length);
		Assert.assertEquals(sessionID, m.getParameters()[0]);
		final IUserInformationCallback userInformationCallback = (IUserInformationCallback)m.getParameters()[1];

		userInformationCallback.onSuccess(user);
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_LOGGED_IN);
		Assert.assertEquals(1, v.size());
		
		// retrieveAllowedExperiments
		controller.retrieveAllowedExperiments();		
		v = this.fakeCommunications.getMethodByName(FakeWlLabCommunication.LIST_EXPERIMENTS);
		Assert.assertEquals(1, v.size());
		m = v.get(0);
		Assert.assertEquals(2, m.getParameters().length);
		Assert.assertEquals(sessionID, m.getParameters()[0]);		
		final IExperimentsAllowedCallback experimentsAllowedCallback = (IExperimentsAllowedCallback)(m.getParameters()[1]);
		
			// failure
        		experimentsAllowedCallback.onFailure(new WlCommException("error retrieving experiments allowed"));
        		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR).size());
        		
        		// success
        		final ExperimentAllowed [] experimentsAllowed = new ExperimentAllowed[]{};
        		experimentsAllowedCallback.onSuccess(experimentsAllowed);
        		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_ALLOWED_EXPERIMENTS_RETRIEVED).size());
        		Assert.assertEquals(1,(this.fakeUIManager.getMethodByName(FakeUIManager.ON_ALLOWED_EXPERIMENTS_RETRIEVED).get(0)).getParameters().length);
        		Assert.assertEquals(experimentsAllowed,(this.fakeUIManager.getMethodByName(FakeUIManager.ON_ALLOWED_EXPERIMENTS_RETRIEVED).get(0)).getParameters()[0]);
		
		// logout
		controller.logout();		
		v = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGOUT);
		Assert.assertEquals(1,v.size());
		m = v.get(0);
		Assert.assertEquals(2,m.getParameters().length);
		Assert.assertEquals(sessionID,m.getParameters()[0]);		
		final IVoidCallback voidCallback = (IVoidCallback)m.getParameters()[1];
		
        		// failure
        		voidCallback.onFailure(new WlCommException("haw haw"));
        		// Was called in the previous "test failure"
        		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_SESSION).size());
        		
        		// success
        		voidCallback.onSuccess();
        		Assert.assertEquals(1,this.fakeUIManager.getMethodByName(FakeUIManager.ON_LOGGED_OUT).size());
	}
	
	public void testFailedExperimentReservation() throws Exception{
		List<Methods> v;
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		
		callback.onFailure(new WlCommException("whatever"));
		
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_RESERVATION);
		Assert.assertEquals(1, v.size());
		
		v = this.fakePollingHandler.getMethodByName(FakePollingHandler.START);
		Assert.assertEquals(0, v.size());
		
		final List<CreateTimerParameters> l = context.controller.getCreateTimerCalled();
		Assert.assertEquals(0, l.size());
	}

	public void testCancellingExperimentReservation() throws Exception{
		List<Methods> v;
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		
		callback.onSuccess(new CancellingReservationStatus());
		
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_ERROR_AND_FINISH_RESERVATION);
		Assert.assertEquals(1, v.size());
		
		v = this.fakePollingHandler.getMethodByName(FakePollingHandler.START);
		Assert.assertEquals(0, v.size());
		
		final List<CreateTimerParameters> l = context.controller.getCreateTimerCalled();
		Assert.assertEquals(0, l.size());
	}
	
	public void testWaitingInstancesExperimentReservation() throws Exception{
		List<Methods> v;
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		
		callback.onSuccess(new WaitingInstancesReservationStatus());
		
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_WAITING_INSTANCES);
		Assert.assertEquals(1, v.size());
		
		v = this.fakePollingHandler.getMethodByName(FakePollingHandler.START);
		Assert.assertEquals(1, v.size());
		
		final List<CreateTimerParameters> v2 = context.controller.getCreateTimerCalled();
		Assert.assertEquals(1, v2.size());
		final CreateTimerParameters ctp = v2.get(0);
		Assert.assertEquals( WlLabControllerTest.WAITING_INSTANCES_MIN_POLL_TIME, ctp.millis);
	}

	public void testWaitingExperimentReservation() throws Exception{
		List<Methods> v;
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		
		callback.onSuccess(new WaitingReservationStatus());
		
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_WAITING_RESERVATION);
		Assert.assertEquals(1, v.size());
		
		v = this.fakePollingHandler.getMethodByName(FakePollingHandler.START);
		Assert.assertEquals(1, v.size());
		
		final List<CreateTimerParameters> v2 = context.controller.getCreateTimerCalled();
		Assert.assertEquals(1, v2.size());
		final CreateTimerParameters ctp = v2.get(0);
		Assert.assertEquals( WlLabControllerTest.WAITING_MIN_POLL_TIME, ctp.millis);
	}

	public void testWaitingConfirmationExperimentReservation() throws Exception{
		List<Methods> v;
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		
		callback.onSuccess(new WaitingConfirmationReservationStatus());
		
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_WAITING_RESERVATION_CONFIRMATION);
		Assert.assertEquals(1, v.size());
		
		v = this.fakePollingHandler.getMethodByName(FakePollingHandler.START);
		Assert.assertEquals(1, v.size());
		
		final List<CreateTimerParameters> v2 = context.controller.getCreateTimerCalled();
		Assert.assertEquals(1, v2.size());
		final CreateTimerParameters ctp = v2.get(0);
		Assert.assertEquals( WlLabControllerTest.WAITING_CONFIRMATION_POLL_TIME, ctp.millis);
	}
	
	public void testConfirmedExperimentReservation() throws Exception{
		List<Methods> v;
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		
		callback.onSuccess(new ConfirmedReservationStatus(100));
		
		// v = this.fakeCommunications.getMethodByName(FakeWebLabCommunication.SEND_FILE);
		// Assert.assertEquals(1, v.size());
		
		// final Methods m = v.get(0);
		// Assert.assertEquals(3, m.getParameters().length);
		
		// Assert.assertEquals(context.sessionID, m.getParameters()[0]);
		// final VoidCallback vc = (VoidCallback)m.getParameters()[2];
		// vc.onSuccess();
		                  
		v = this.fakeUIManager.getMethodByName(FakeUIManager.ON_EXPERIMENT_RESERVED);
		Assert.assertEquals(1, v.size());
		
		v = this.fakePollingHandler.getMethodByName(FakePollingHandler.START);
		Assert.assertEquals(1, v.size());
		
		final List<CreateTimerParameters> l = context.controller.getCreateTimerCalled();
		Assert.assertEquals(0, l.size());
	}
	
	public void testSendCommand() throws Exception{
		List<Methods> v;
		Methods m;
		final ReservationContext context = this.createConfirmedReservationContext();
		
		final String commandMsg = "First command";
		final MyCommand myCommand = new MyCommand(commandMsg);
		final IResponseCommandCallback commandCallback = new IResponseCommandCallback(){
		    @Override
			public void onSuccess(ResponseCommand responseCommand) {
		    }

		    @Override
			public void onFailure(WlCommException e) {
		    }
		}; 
		
		context.controller.sendCommand(myCommand, commandCallback);
		
		v = this.fakeCommunications.getMethodByName(FakeWlLabCommunication.SEND_COMMAND);
		Assert.assertEquals(1, v.size());
		
		m = v.get(0);
		Assert.assertEquals(3, m.getParameters().length);
		Assert.assertEquals(context.sessionID, m.getParameters()[0]);
		Assert.assertEquals(myCommand, m.getParameters()[1]);
		
		Assert.assertTrue(m.getParameters()[2] instanceof IResponseCommandCallback);
		final IResponseCommandCallback callback = (IResponseCommandCallback)m.getParameters()[2];
		
		Assert.assertEquals(commandCallback, callback);
	}
	
	/*
	 * Auxiliar methods
	 */
	
	private Map<String, String> createConfiguration(){
		final Map<String, String> map = new HashMap<String, String>();
		map.put(WlLabController.WAITING_INSTANCES_MIN_POLLING_TIME_PROPERTY, ""+WlLabControllerTest.WAITING_INSTANCES_MIN_POLL_TIME);
		map.put(WlLabController.WAITING_INSTANCES_MAX_POLLING_TIME_PROPERTY, ""+WlLabControllerTest.WAITING_INSTANCES_MAX_POLL_TIME);
		map.put(WlLabController.WAITING_MIN_POLLING_TIME_PROPERTY, ""+WlLabControllerTest.WAITING_MIN_POLL_TIME);
		map.put(WlLabController.WAITING_MAX_POLLING_TIME_PROPERTY, ""+WlLabControllerTest.WAITING_MAX_POLL_TIME);
		map.put(WlLabController.WAITING_CONFIRMATION_POLLING_TIME_PROPERTY, ""+WlLabControllerTest.WAITING_CONFIRMATION_POLL_TIME);
		return map;
	}
	
	private FakeWebLabController createController() {
		this.configurationManager = new FakeConfiguration(this.createConfiguration());
		this.fakeCommunications = new FakeWlLabCommunication();
		this.fakeUIManager = new FakeUIManager();
		this.fakePollingHandler = new FakePollingHandler();
			
		final FakeWebLabController controller = new FakeWebLabController(
				this.configurationManager,
				this.fakeCommunications,
				this.fakeUIManager,
				this.fakePollingHandler
			);
		return controller;
	}
	
	private Experiment createExperiment(){
		final Experiment experiment = new Experiment();
		experiment.setCategory(new Category("Dummy experiments"));
		experiment.setName("ud-dummy");
		return experiment;
	}	
	
	/*
	 * Reservation handling
	 */
	private class ReservationContext{
		public IReservationCallback reservationCallback;
		public FakeWebLabController controller;
		public SessionID sessionID;
	}
	
	private ReservationContext createReservationContext() throws Exception{
		final ReservationContext context = new ReservationContext();
		
		Methods m;
		List<Methods> v;
		
		final User user = new User("porduna", "Pablo Orduña Fernández", "porduna@tecnologico.deusto.es", new Role("student"));
		
		// Data creation
		final SessionID sessionID = new SessionID("something");
		context.sessionID = sessionID;
		
		final Experiment experiment = this.createExperiment();
		
		final ExperimentAllowed [] experimentsAllowed = new ExperimentAllowed[]{
				new ExperimentAllowed(experiment, 100)
		};
		
		// Arriving reservation state
		final FakeWebLabController controller = this.createController();
		final FakeUIManager uimanager  = controller.getFakeUIManager();
		context.controller = controller;
		
		controller.login("whatever", "whatever");
		m = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.LOGIN).get(0); 
		final ISessionIdCallback sic = (ISessionIdCallback)m.getParameters()[2];
		sic.onSuccess(sessionID);
		m = this.fakeCommunications.getMethodByName(FakeWlCommonCommunication.GET_USER_INFORMATION).get(0);
		final IUserInformationCallback uic = (IUserInformationCallback)m.getParameters()[1];
		uic.onSuccess(user);

		controller.retrieveAllowedExperiments();
		m = this.fakeCommunications.getMethodByName(FakeWlLabCommunication.LIST_EXPERIMENTS).get(0); 
		final IExperimentsAllowedCallback eac = (IExperimentsAllowedCallback)(m).getParameters()[1];
		eac.onSuccess(experimentsAllowed);
		
		controller.chooseExperiment(experimentsAllowed[0]);
		Assert.assertEquals(1, uimanager.getMethodByName(FakeUIManager.ON_EXPERIMENT_CHOOSEN).size());
		
		// Reservation test itself
		controller.reserveExperiment(experiment.getExperimentUniqueName());
		v = this.fakeCommunications.getMethodByName(FakeWlLabCommunication.RESERVE_EXPERIMENT);
		Assert.assertEquals(1, v.size());
		m = v.get(0); 
		Assert.assertEquals(3, m.getParameters().length);
		Assert.assertEquals(sessionID, m.getParameters()[0]);
		Assert.assertEquals(experiment.getExperimentUniqueName(), m.getParameters()[1]);
		final IReservationCallback callback = (IReservationCallback)m.getParameters()[2];
		context.reservationCallback = callback;
		return context;
	}	
	
	private ReservationContext createConfirmedReservationContext() throws Exception{
		final ReservationContext context = this.createReservationContext();
		final IReservationCallback callback = context.reservationCallback;
		callback.onSuccess(new ConfirmedReservationStatus(100));
		return context;
	}
		
	/*
	 * Auxiliar structures and classes
	 */
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
	
	private class CreateTimerParameters{
		public int millis;
		public CreateTimerParameters(int millis){
			this.millis = millis;
		}
	}
	
	private class FakeWebLabController extends WlLabController{
	    	private final FakeUIManager uimanager;
	    	
		public FakeWebLabController(
				IConfigurationManager configurationManager,
				FakeWlLabCommunication fakeCommunications,
				FakeUIManager fakeUIManager,
				FakePollingHandler fakePollingHandler) {
			super(configurationManager, fakeCommunications, fakePollingHandler, false);
			this.uimanager = fakeUIManager;
			this.setUIManager(fakeUIManager);
		}

		private final List<CreateTimerParameters> createTimerCalled = new Vector<CreateTimerParameters>();
		
		public List<CreateTimerParameters> getCreateTimerCalled(){
			return this.createTimerCalled;
		}
		
		@Override
		protected void createTimer(int millis, IControllerRunnable runnable){
			this.createTimerCalled.add(new CreateTimerParameters(
						millis
					));
		}
		
		public FakeUIManager getFakeUIManager(){
		    return this.uimanager;
		}
	}
	
	private class MyCommand extends Command{
		private final String s;
		public MyCommand(String s){
			this.s = s;
		}
		
		@Override
		public String getCommandString() {
			return this.s;
		}
	}
}
