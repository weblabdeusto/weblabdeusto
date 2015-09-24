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
* Author: Pablo Orduña <pablo.orduna@deusto.es>
*
*/

package es.deusto.weblab.client.experiments.labview.ui;

public class LabViewObjectGenerator {

	public static String generate(int height, int width, String viName, String server, String version){
		final StringBuilder builder = new StringBuilder();
		
		final String control = "true";
		final LabViewVersionArguments args = LabViewVersionArguments.getVersion(version);
		if(args == null)
			return "LabVIEW version \"" + version + "\" not supported by current client";
		
		// XXX: maybe through the properties of the configuration.js we could do this as well
		final String classId = args.getClassId();
		final String codeBase = args.getCodeBase();
		final String pluginsPage = args.getPluginsPage();
		
		builder.append("<OBJECT ID=\"LabVIEWControl\" CLASSID=\"" + classId + "\" WIDTH=" + width + " HEIGHT=" + width + " CODEBASE=\"" + codeBase + "\">\n");
		builder.append("<PARAM name=\"server\" value=\"" + server + "\">\n");
		builder.append("<PARAM name=\"LVFPPVINAME\" value=\"" + viName + "\">\n");
		builder.append("<PARAM name=\"REQCTRL\" value=" + control + ">\n");
		builder.append("<EMBED SRC=\"" + server + viName + "\" LVFPPVINAME=\"" + viName + "\" REQCTRL=" + control + " TYPE=\"application/x-labviewrpvi90\" WIDTH=" + width + " HEIGHT=" + height + " PLUGINSPAGE=\"" + pluginsPage + "\">\n");
		builder.append("</EMBED>\n");
		builder.append("</OBJECT>\n");
		
		return builder.toString();
	}
}
