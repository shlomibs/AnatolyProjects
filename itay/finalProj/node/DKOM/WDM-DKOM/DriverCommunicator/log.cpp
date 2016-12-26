#include"log.h"
#include<fstream>

Log::Log(const char* FileName)
{
	this->FileName = FileName;
}

Log::Log():Log::Log("log.log")
{}

Log::Log(char* FileName):Log::Log((const char*)FileName)
{}

Log::~Log()
{
	delete[] FileName;
	FileName = NULL;
}

void Log::Write(char* Text)
{
	std::ofstream logger(FileName, std::ios::app);
	logger << Text;
	logger.close();
}

void Log::WriteLine(char* Text)
{
	std::ofstream logger(FileName, std::ios::app);
	logger << Text << std::endl;
	logger.close();
}

void Log::Write(const char* Text)
{
	std::ofstream logger(FileName, std::ios::app);
	logger << Text;
	logger.close();
}

void Log::WriteLine(const char* Text)
{
	std::ofstream logger(FileName, std::ios::app);
	logger << Text << std::endl;
	logger.close();
}

void Log::Clear()
{
	std::ofstream logger(FileName);
	logger.close();
}