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

package es.deusto.weblab.client.lab.experiments.plugins.es.deusto.weblab.labview.ui;

import java.util.HashMap;
import java.util.Map;

class LabViewVersionArguments{
	private final String classId;
	private final String codeBase;
	private final String pluginsPage;
	
	private static Map<String, LabViewVersionArguments> byVersion = new HashMap<String, LabViewVersionArguments>();
	static{
		final String classId = "CLSID:A40B0AD4-B50E-4E58-8A1D-8544233807B1";
		final String codeBase = "ftp://ftp.ni.com/support/labview/runtime/windows/9.0/LVRTE90min.exe";
		final String pluginsPage = "http://digital.ni.com/express.nsf/bycode/exck2m";
		byVersion.put("2009", new LabViewVersionArguments(classId, codeBase, pluginsPage)); 
	}
	
	static LabViewVersionArguments getVersion(String version){
		return byVersion.get(version);
	}
	
	private LabViewVersionArguments(String classId, String codeBase,String pluginsPage) {
		this.classId = classId;
		this.codeBase = codeBase;
		this.pluginsPage = pluginsPage;
	}

	String getClassId() {
		return this.classId;
	}

	String getCodeBase() {
		return this.codeBase;
	}

	String getPluginsPage() {
		return this.pluginsPage;
	}
}