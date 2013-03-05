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

package es.deusto.weblab.server;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Arrays;
import java.util.Collection;
import java.util.Enumeration;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@SuppressWarnings("serial")
public class RequestForwarder extends HttpServlet{

	private final String host = "localhost";
	
	@Override
	public void doHead(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		forwardRequest(req, resp);
	}

	@Override
	public void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		forwardRequest(req, resp);
	}

	@Override
	public void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException{
		forwardRequest(req, resp);
	}
	
	private void forwardRequest(HttpServletRequest req, HttpServletResponse resp) throws IOException {
		final HttpURLConnection serverConnection = startRequest(req);

		if(req.getMethod().equals("POST"))
			this.forwardStreamToEnd(req.getInputStream(), serverConnection.getOutputStream());
		
		int statusCode;
		try{
			statusCode = serverConnection.getResponseCode();
		}catch(IOException e) {
			statusCode = serverConnection.getResponseCode();
		}
		resp.setStatus(statusCode);
		
		final boolean isError = (statusCode / 100) % 1000 == 4 || (statusCode / 100) % 1000 == 5; 
		
	    for(final String header : serverConnection.getHeaderFields().keySet()){
	    	for(final String value : serverConnection.getHeaderFields().get(header)) { 
		        if(isValidHeader(header) && value != null){
		        	if(header.startsWith("Set-Cookie")) {
		        		resp.addHeader(header, value.replaceAll("path=/[^;]*", "path=/"));
		        	} else {
		        		resp.addHeader(header, value);
		        	}
		        }
	    	}
	    }
		resp.addHeader("Connection", "close");
		resp.addHeader("X-Foo", "bar");
		
		this.forwardStreamToSize(isError?serverConnection.getErrorStream():serverConnection.getInputStream(), resp.getOutputStream(), serverConnection.getContentLength());
	}

	private HttpURLConnection startRequest(HttpServletRequest req) throws IOException {
		final String queryString = (req.getQueryString() != null)?"?"+req.getQueryString():"";
		final HttpURLConnection serverConnection = (HttpURLConnection)new URL("http", this.host, req.getRequestURI()+queryString).openConnection();
		serverConnection.setDoOutput(true);
		serverConnection.setDoInput(true);
		serverConnection.setUseCaches(false);
		
	    final Enumeration<?> headersIn = req.getHeaderNames();
	    while(headersIn.hasMoreElements()){
	    	final String header = (String)headersIn.nextElement();
	    	if(isValidHeader(header))
	    	    serverConnection.addRequestProperty(header, req.getHeader(header));
	    }
		serverConnection.addRequestProperty("Connection", "close");
		serverConnection.addRequestProperty("X-Faa", "ber");
		serverConnection.connect();
		return serverConnection;
	}

	private final static Collection<String> badHeaders = Arrays.asList("host", "connection", "keep-alive");
	
	private boolean isValidHeader(String header) {
	    return header != null && !RequestForwarder.badHeaders.contains(header.toLowerCase());
	}

	private void forwardStreamToEnd(final InputStream is, final OutputStream os) throws IOException {
		final BufferedInputStream bis = new BufferedInputStream(is);
		final BufferedOutputStream bos = new BufferedOutputStream(os);
    	final byte [] buffer = new byte [4096];
    	int bytesRead;
    	do{
    		bytesRead = bis.read(buffer);
    		
    		if(bytesRead > 0)
    		    bos.write(buffer, 0, bytesRead);
    	}while(bytesRead != -1);
    	bis.close();
    	bos.flush();
    	bos.close();
    }

	private void forwardStreamToSize(final InputStream is, final OutputStream os, int size) throws IOException {
		final BufferedInputStream bis = new BufferedInputStream(is);
		final BufferedOutputStream bos = new BufferedOutputStream(os);
    	final byte [] buffer = new byte [4096];
    	int bytesRead;
    	int totalRead = size;
    	do{
    		bytesRead = bis.read(buffer);
    		if(bytesRead > 0){
    		    bos.write(buffer, 0, bytesRead);
    		    totalRead -= bytesRead;
    		}
    	}while(bytesRead != -1 && totalRead > 0);
    	bis.close();
    	bos.flush();
    	bos.close();
    }
}
