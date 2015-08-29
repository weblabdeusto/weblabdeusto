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
package es.deusto.weblab.client.ui.widgets;

import junit.framework.Assert;

import com.google.gwt.junit.client.GWTTestCase;

import es.deusto.weblab.client.ui.widgets.WlUtil;

public class WlUtilTest extends GWTTestCase  {
	
	public void testEscape(){
		/*
		assertEquals("%41", WlUtil.escape("A"));
		assertEquals("%20", WlUtil.escape(" "));
		assertEquals("%0d", WlUtil.escape("\r"));
		*/
		Assert.assertEquals("A", WlUtil.escape("A"));
		Assert.assertEquals(" ", WlUtil.escape(" "));
		Assert.assertEquals("\r", WlUtil.escape("\r"));
		Assert.assertEquals("&lt;", WlUtil.escape("<"));
		Assert.assertEquals("&lt;&lt;", WlUtil.escape("<<"));
		Assert.assertEquals("&gt;", WlUtil.escape(">"));
		Assert.assertEquals("&quot;", WlUtil.escape("\""));
		Assert.assertEquals("&lt;a href=&quot;whatever&quot;&gt;&lt;/a&gt;", WlUtil.escape("<a href=\"whatever\"></a>"));
	}
	
	public void testEscapeNotQuote(){
		Assert.assertEquals("A", WlUtil.escapeNotQuote("A"));
		Assert.assertEquals(" ", WlUtil.escapeNotQuote(" "));
		Assert.assertEquals("\r", WlUtil.escapeNotQuote("\r"));
		Assert.assertEquals("&lt;", WlUtil.escapeNotQuote("<"));
		Assert.assertEquals("&lt;&lt;", WlUtil.escapeNotQuote("<<"));
		Assert.assertEquals("&gt;", WlUtil.escapeNotQuote(">"));
		Assert.assertEquals("\"", WlUtil.escapeNotQuote("\""));
		Assert.assertEquals("&lt;a href=\"whatever\"&gt;&lt;/a&gt;", WlUtil.escapeNotQuote("<a href=\"whatever\"></a>"));
	}
	
	@Override
	public String getModuleName() {
		return "es.deusto.weblab.WebLabClient";
	}
}
