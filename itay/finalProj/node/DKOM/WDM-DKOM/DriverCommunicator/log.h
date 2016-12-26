#ifndef LOG_H
#define LOG_H
#include<iostream>

class Log
{
private:
	const char* FileName;
public:
	Log();
	Log(const char* FileName);
	Log(char* FileName);
	~Log();
	void Write(char* Text);
	void WriteLine(char* Text);
	void Write(const char* Text);
	void WriteLine(const char* Text);
	void Clear();
};
#endif