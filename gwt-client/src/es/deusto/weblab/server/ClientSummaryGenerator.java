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
* Author: FILLME
*
*/

package es.deusto.weblab.server;

import java.io.PrintStream;

import es.deusto.weblab.client.lab.experiments.EntryRegistry;
import es.deusto.weblab.client.lab.experiments.ExperimentParameter;
import es.deusto.weblab.client.lab.experiments.IExperimentCreatorFactory;
import es.deusto.weblab.client.lab.experiments.IHasExperimentParameters;

public class ClientSummaryGenerator {
	public static void main(String [] args) throws Exception {
		
		ExperimentParameter []  defaultExperimentParameters = new ExperimentParameter[] {
			new ExperimentParameter("experiment.picture", ExperimentParameter.Type.string, "Path to the experiment pictures"),	
			new ExperimentParameter("experiment.info.link", ExperimentParameter.Type.string, "Link to point in the information"),
			new ExperimentParameter("experiment.info.description", ExperimentParameter.Type.string, "Description message"),
			new ExperimentParameter("experiment.reserve.button.shown", ExperimentParameter.Type.bool, "Show the reserve button or not"),
		};

		final PrintStream ps = new PrintStream("clients_summary.txt");
		try {
			for(IExperimentCreatorFactory factory : EntryRegistry.creatorFactories) {
				ps.println("Type::::" + factory.getCodeName());
				for (ExperimentParameter parameter : defaultExperimentParameters)
					generateParameter(ps, factory, parameter);
				
				if (factory instanceof IHasExperimentParameters) {
					ExperimentParameter [] parameters = ((IHasExperimentParameters)factory).getParameters();
					if (parameters != null)
						for(ExperimentParameter parameter : parameters)
							generateParameter(ps, factory, parameter);
				}
			}
		} finally {
			ps.close();
		}
	}

	private static void generateParameter(final PrintStream ps,
			IExperimentCreatorFactory factory, ExperimentParameter parameter)
			throws Exception {
		String description = parameter.getDescription();
		if (description.indexOf("::::") >= 0) {
			throw new Exception("Factory " + factory.getCodeName() + " contains :::: in its description");
		}
		description = description.replace("\n", "\\n").replace("\r", "\\r");
		ps.println("Parameter::::" + parameter.getName() + "::::" + parameter.getType() + "::::" + description);
	}
}
