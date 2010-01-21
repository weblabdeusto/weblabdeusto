# file: Makefile

all:
	gmcs -t:library -r:System.Runtime.Remoting -r:CookComputing.XmlRpcV2.dll WebLabDeustoExperimentServer.cs LabViewWrapper.cs -out:WebLabDeustoExperimentServer.dll
	gmcs -r:WebLabDeustoExperimentServer.dll DummyExperimentServer.cs -out:DummyExperimentServer.exe

clean:
	rm -f WebLabDeustoExperimentServer.dll DummyExperimentServer.exe
