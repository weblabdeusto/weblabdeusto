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
*
*/ 
package es.deusto.weblab.client.dto;

public class SessionID {
	private final String realId;
	
	public SessionID(String realId){
		this.realId = realId;
	}

	public String getRealId() {
		return this.realId;
	}
	
	public boolean isNull() {
		return false;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#hashCode()
	 */
	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((this.realId == null) ? 0 : this.realId.hashCode());
		return result;
	}

	/* (non-Javadoc)
	 * @see java.lang.Object#equals(java.lang.Object)
	 */
	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		SessionID other = (SessionID) obj;
		if (this.realId == null) {
			if (other.realId != null)
				return false;
		} else if (!this.realId.equals(other.realId))
			return false;
		return true;
	}
}
