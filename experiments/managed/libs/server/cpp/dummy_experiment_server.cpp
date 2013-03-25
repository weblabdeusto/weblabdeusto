//
// Copyright (C) 2005-2009 University of Deusto
// All rights reserved.
//
// This software is licensed as described in the file COPYING, which
// you should have received as part of this distribution.
//
// This software consists of contributions made by many individuals,
// listed below:
//
// Author: Luis Rodriguez <luis.rodriguez@opendeusto.es>
//         Jaime Irurzun <jaime.irurzun@gmail.com>
//

#include "weblabdeusto_experiment_server.hpp"

#include <iostream>


class DummyExperimentServer : public ExperimentServer
{
public:

	virtual std::string onStartExperiment()
	{
		return "ok";
	}

	virtual std::string onSendFile(std::string const & encoded_file, std::string const & fileinfo)
	{
		return "ok";
	}
	
	virtual std::string onSendCommand(std::string const & command)
	{
		return "ok";
	}
	
	virtual std::string onDispose()
	{
		return "ok";
	}
};



int main(int argc, char const * argv[])
{
	DummyExperimentServer testServer;
	testServer.launch(12345, "rpc_log.txt");
}
