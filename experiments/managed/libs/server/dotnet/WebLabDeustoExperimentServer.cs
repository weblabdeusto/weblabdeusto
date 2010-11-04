using System;
using System.IO;
using System.Runtime.Remoting;
using System.Runtime.Remoting.Channels;
using System.Runtime.Remoting.Channels.Http;
using CookComputing.XmlRpc;

namespace WebLabDeusto{

    public interface ExperimentServer {
        string SendFile(byte [] file, string fileInfo);
        string SendCommand(string command);
        void StartExperiment();
        void Dispose();
    }

    internal class WebLabDotNetDummy : MarshalByRefObject 
    { 
        private static ExperimentServer experimentServer;

        public static ExperimentServer Server{
            set{
                experimentServer = value;
            }
        }

        [XmlRpcMethod("Util.test_me")] 
        public string test_me(string message)
        { 
            return message;
        }

        [XmlRpcMethod("Util.send_file_to_device")]
        public string send_file_to_device(string fileEncodedWithBase64, string fileInfo){
            byte [] decodedBytes = Convert.FromBase64String (fileEncodedWithBase64);
            return experimentServer.SendFile(decodedBytes, fileInfo);
        }

        [XmlRpcMethod("Util.send_command_to_device")]
        public string send_command_to_device(string command){
            return experimentServer.SendCommand(command);
        }

        [XmlRpcMethod("Util.start_experiment")]
        public string start_experiment(){
            experimentServer.StartExperiment();
            return "ok";
        }

        [XmlRpcMethod("Util.dispose")]
        public string dispose(){
            experimentServer.Dispose();
            return "ok";
        }
    }

    public class Runner{

        private readonly ExperimentServer experimentServer;
        private readonly int port;
        private readonly string servicePath;

        public Runner(ExperimentServer experimentServer, int port, string servicePath){
            this.experimentServer = experimentServer;
            this.port = port;
            this.servicePath = servicePath;
        }

        public void Start(){
            WebLabDotNetDummy.Server = this.experimentServer;

            IServerChannelSinkProvider formatter = new CookComputing.XmlRpc.XmlRpcServerFormatterSinkProvider();
            HttpServerChannel channel = new HttpServerChannel("WebLab-Deusto", this.port, formatter);
            ChannelServices.RegisterChannel(channel, false);

            RemotingConfiguration.RegisterWellKnownServiceType(
                typeof(WebLabDeusto.WebLabDotNetDummy), 
                this.servicePath,
                WellKnownObjectMode.Singleton
            ); 
        }
    }

}
