#include "boost/python.hpp"
#include "boost/detail/lightweight_test.hpp"
#include <iostream>

namespace python = boost::python;

int run()
{
	return 0;
}

#define SCRIPT_PATH "/mclinker_src/tools/mcld/lib/BuildGraph.py"

void exec_file_test()
{
  	std::string const script = "/mclinker_src/tools/mcld/lib/BuildGraph.py";
	char progname[] = "buildgraph";
	Py_SetProgramName(progname);
	Py_Initialize();
	PyRun_SimpleString("import sys; sys.path.append('/mclinker_src/tools/mcld/lib/')");
	std::cout<<"Running a file..."<<script<<"..."<<"\n";
	
	python::object main = python::import("__main__");
	python::object global(main.attr("__dict__"));
	python::object result = python::exec_file(SCRIPT_PATH, global, global);
	std::cout<<"end of exec_file_test.."<<"\n";
}

int run2()
{
	exec_file_test();
	return 0;
}
