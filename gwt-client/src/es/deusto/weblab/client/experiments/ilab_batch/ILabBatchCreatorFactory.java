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
*		  Luis Rodriguez <luis.rodriguez@opendeusto.es>
*/

package es.deusto.weblab.client.experiments.ilab_batch;

import com.google.gwt.core.client.GWT;
import com.google.gwt.core.client.RunAsyncCallback;

import es.deusto.weblab.client.configuration.IConfigurationRetriever;
import es.deusto.weblab.client.experiments.ilab_batch.ui.ILabBatchExperiment;
import es.deusto.weblab.client.lab.experiments.ExperimentCreator;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.IExperimentLoadedCallback;
import es.deusto.weblab.client.lab.experiments.ExperimentFactory.MobileSupport;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.ExperimentParameterDefault;
import es.deusto.weblab.client.lab.experiments.IBoardBaseController;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.IHasExperimentParameters;

public class ILabBatchCreatorFactory implements IExperimentCreatorFactory, IHasExperimentParameters {

	public static final ExperimentParameter ARCHIVE = new ExperimentParameter("archive", ExperimentParameter.Type.string, "iLab archive file");
	public static final ExperimentParameter CODE = new ExperimentParameter("code", ExperimentParameter.Type.string, "iLab class file");
	public static final ExperimentParameter LAB_SERVER_ID = new ExperimentParameter("lab_server_id", ExperimentParameter.Type.string, "iLab lab server id");
	public static final ExperimentParameterDefault SERVICE_BROKER = new ExperimentParameterDefault("service_broker", "iLab Service Broker relative URL", "/weblab/web/ilab/");
	
	@Override
	public String getCodeName() {
		return "ilab-batch";
	}

	@Override
	public ExperimentCreator createExperimentCreator(final IConfigurationRetriever configurationRetriever) {
		return	new ExperimentCreator(MobileSupport.disabled, getCodeName()){
			@Override
			public void createWeb(final IBoardBaseController boardController, final IExperimentLoadedCallback callback) {
				GWT.runAsync(new RunAsyncCallback() {
					@Override
					public void onSuccess() {
						callback.onExperimentLoaded(new ILabBatchExperiment(
								configurationRetriever,
								boardController
							));
					}
					
					@Override
					public void onFailure(Throwable e){
						callback.onFailure(e);
					}
				});
			}
		};
	}

	@Override
	public ExperimentParameter[] getParameters() {
		return new ExperimentParameter[] { ARCHIVE, CODE, LAB_SERVER_ID, SERVICE_BROKER };
	}
}
