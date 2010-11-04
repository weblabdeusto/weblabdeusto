using System;
using System.IO;

class SampleExperimentServer : WebLabDeusto.ExperimentServer {
        public string SendFile(byte [] file, string fileInfo){
            int length = file.Length;
            Console.WriteLine("File received: {0}", length);
            return "File received " + length;
        }

        public string SendCommand(string command){
            Console.WriteLine("Command received: {0}", command);
            return "Command received: " + command;
        }

        public void StartExperiment(){
            Console.WriteLine("Experiment started");
        }

        public void Dispose(){
            Console.WriteLine("Experiment disposed");
        }
}

class Tester{
    public static void Main(){
        WebLabDeusto.Runner runner = new WebLabDeusto.Runner(
                                            new SampleExperimentServer(),
                                            5678,
                                            "weblab"
                                    );
        runner.Start();
        Console.WriteLine("Press to shutdown"); 
        Console.ReadLine(); 
    
    }
}

