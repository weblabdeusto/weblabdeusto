namespace WebLabDeusto{

    public delegate string FileSentHandler(byte [] file, string fileInfo);
    public delegate string CommandSentHandler(string command);
    public delegate void ExperimentStartedHandler();
    public delegate void DisposedHandler();

    internal class LabViewExperiment : ExperimentServer{

        private readonly LabViewExperimentRunner runner;

        public LabViewExperiment(LabViewExperimentRunner runner){
            this.runner = runner;
        }

        public string SendFile(byte [] file, string fileInfo){
            return this.runner.OnSendFile(file, fileInfo);
        }

        public string SendCommand(string command){
            return this.runner.OnSendCommand(command);
        }

        public void StartExperiment(){
            this.runner.OnStartExperiment();
        }

        public void Dispose(){
            this.runner.OnDispose();
        }
    }

    public class LabViewExperimentRunner{

        private readonly Runner runner;

        public LabViewExperimentRunner(int port, string servicePath){
            ExperimentServer experiment = new LabViewExperiment(this);
            this.runner = new Runner(experiment, port, servicePath);
            this.runner.Start();
        }

        public LabViewExperimentRunner(int port) : this(port, "weblab") {}
        
        public event FileSentHandler FileSent;
        public event CommandSentHandler CommandSent;
        public event ExperimentStartedHandler ExperimentStarted;
        public event DisposedHandler Disposed;

        internal string OnSendCommand(string command){
            return CommandSent(command);
        }

        internal string OnSendFile(byte [] file, string fileInfo){
            return FileSent(file, fileInfo);
        }

        internal void OnStartExperiment(){
            ExperimentStarted();
        }

        internal void OnDispose(){
            Disposed();
        }
    }
}

