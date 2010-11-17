package es.deusto.weblab.experimentservers;

import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.XmlRpcServerConfigImpl;
import org.apache.xmlrpc.webserver.WebServer;

public class Launcher {
	
	
	private int port;
	private IExperimentServer experimentServer;
	
	public Launcher(int port, IExperimentServer experimentServer){
		this.port        = port;
		this.experimentServer = experimentServer;
	}
	
	// TODO: improve this "throws Exception"
	public void start() throws Exception{
		WebServer webServer = new WebServer(this.port);
		XmlRpcServer xmlRpcServer = webServer.getXmlRpcServer();
		PropertyHandlerMapping phm = new PropertyHandlerMapping();
		
		ExperimentServerXMLRPC.IExperimentServerHolder.initialize(this.experimentServer);
		
		phm.addHandler("Util",
					ExperimentServerXMLRPC.class
				);
		
		xmlRpcServer.setHandlerMapping(phm);
		XmlRpcServerConfigImpl serverConfig =
			(XmlRpcServerConfigImpl) xmlRpcServer.getConfig();
		serverConfig.setEnabledForExtensions(false);
		serverConfig.setContentLengthOptional(false);
		
		webServer.start();
		System.out.println("Running XML-RPC server on port "+this.port+"...\n");
	}
}
