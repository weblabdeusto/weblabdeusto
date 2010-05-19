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
* Author: FILLME
*
*/

package es.deusto.weblab.client.admin.comm;

import es.deusto.weblab.client.comm.IWlCommonSerializer;
import es.deusto.weblab.client.comm.WlCommonCommunication;
import es.deusto.weblab.client.configuration.IConfigurationManager;

public class WlAdminCommunication extends WlCommonCommunication implements IWlAdminCommunication {
	
	public static final String WEBLAB_ADMIN_SERVICE_URL_PROPERTY = "weblab.service.admin.url";
	public static final String DEFAULT_WEBLAB_ADMIN_SERVICE_URL = "/weblab/admin/json/";

	public WlAdminCommunication(IConfigurationManager configurationManager) {
		super(configurationManager);
	}

	@Override
	protected IWlCommonSerializer createSerializer() {
		return new WlAdminSerializerJSON();
	}

}
