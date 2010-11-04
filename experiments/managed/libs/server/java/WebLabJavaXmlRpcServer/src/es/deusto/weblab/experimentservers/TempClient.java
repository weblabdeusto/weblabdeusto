package es.deusto.weblab.experimentservers;

import java.net.URL;

import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import org.apache.xmlrpc.client.XmlRpcCommonsTransportFactory;

class TempClient {
	public static void main(String [] args) throws Exception{
		 XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
		 config.setServerURL(new URL("http://127.0.0.1:8080/xmlrpc"));
		 config.setEnabledForExtensions(false);
		 config.setConnectionTimeout(60 * 1000);
		 config.setReplyTimeout(60 * 1000);
		 
		 XmlRpcClient client = new XmlRpcClient();
		 client.setTransportFactory(
				new XmlRpcCommonsTransportFactory(client)
			);
		 client.setConfig(config);
		 
		 client.execute("Util.send_command", new Object[]{"hola"});

		 System.out.println("hecho");
	}

}
