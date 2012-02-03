package es.deusto.weblab.server;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class VersionWriter {
	
	private static final String UNDEFINED = "undefined";
	private static final boolean LINK_TO_VERSION = true;
	
	private static String global = UNDEFINED;
	private static String local  = UNDEFINED;
	private static String date   = UNDEFINED;
	
    public static void main(String [] args) throws Exception {
    	
    	if(args.length != 1 || !args[0].endsWith(".js")){
    		System.err.println("Usage: " + VersionWriter.class.getSimpleName() + " file.js");
    		System.exit(-1);
    	}
    	
    	final String filename = args[0];
    	
    	retrieveVersion();
    	if(global == UNDEFINED && local == UNDEFINED){
    		System.err.println("Error retrieving version");
    		System.exit(-2);
    	}
    		
    	retrieveDate();
    	if(date == UNDEFINED){
    		System.err.println("Error retrieving date");
    		System.exit(-3);
    	}
    	
    	final String message;
    	
    	if(LINK_TO_VERSION)
    		message = "var wlVersionMessage = \"WebLab-Deusto r<a href=\\\"http://code.google.com/p/weblabdeusto/source/list?r=" + global + "\\\">" + local + "</a> | Last update: " + date + "\";";
    	else
    		message = "var wlVersionMessage = \"WebLab-Deusto r<a href=\\\"http://code.google.com/p/weblabdeusto/source/list\\\">" + local + "</a> | Last update: " + date + "\";";
    	
    	PrintStream ps = new PrintStream(filename);
    	ps.print(message);
    	ps.flush();
    	ps.close();
    }

	private static void retrieveVersion() throws Exception{
		final ProcessBuilder builder = new ProcessBuilder("hg","identify","-ni");
    	final Process process = builder.start();
    	final int code = process.waitFor();
    	if(code == 0){
    		final BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
    		final String [] version = reader.readLine().split(" ");
    		global = version[0].trim();
    		local = version[1].trim();
    		if(global.endsWith("+")){ // If something changed
    			global = global.substring(0, global.length() - 1);
    			local  = local.substring(0,  local.length() - 1);
    		}
    	}else{
    		final BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
    		String line;
    		while((line = reader.readLine()) != null)
    			System.err.println(line);    		
    	}
	}
	
	private static void retrieveDate() throws Exception{
		final ProcessBuilder builder = new ProcessBuilder("hg","log","-r",global,"--template","{date|shortdate}");
    	final Process process = builder.start();
    	final int code = process.waitFor();
    	if(code == 0){
    		final BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
    		String line = reader.readLine();
    		
    		final SimpleDateFormat mercurialFormat = new SimpleDateFormat("yyyy-MM-d");
    		Date parsedDate = mercurialFormat.parse(line);
    		
    		final SimpleDateFormat desiredFormat = new SimpleDateFormat("EEEE, MMMM d, yyyy", Locale.ENGLISH);
    		date = desiredFormat.format(parsedDate);
    	}else{
    		final BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
    		String line;
    		while((line = reader.readLine()) != null)
    			System.err.println(line);
    	}
	}
}
