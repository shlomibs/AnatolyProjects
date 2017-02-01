#include <Windows.h>
#include <stdlib.h>
#include <stdio.h>

using namespace std;

bool GetMsi();
bool Install();
bool SetStartupAsAdmin();

int _cdecl main(char** args, int argc)
{
	if (!GetMsi())
		return -1;
	if (!Install())
		return -2;
	if (!SetStartupAsAdmin())
		return -3;
	return 0;
}

bool GetMsi()
{
	// TODO: download the msi to make the installer smaller
	// that will be in the improvment suggestions for the project
	return true;
}

bool Install()
{
	// install the msi without UI -> silently
	// msiexec / i c : \path\to\package.msi / quiet / qn / norestart / log c : \path\to\install.log PROPERTY1 = value1 PROPERTY2 = value2
	if(system("msiexec /i Data/Installer.msi /quiet /qn /norestart")) // if system(str) != 0 then it failed
		return false;
	return true;
}

bool SetStartupAsAdmin()
{
	HKEY key;
	long result = RegOpenKeyEx(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_READ | KEY_WRITE | KEY_QUERY_VALUE, &key);
	if (result != ERROR_SUCCESS)
		return false;

	char cwd[1000];
	GetCurrentDirectory(sizeof(cwd), cwd);
	char path[1024];
	sprintf(path, cwd, "\\Manager.exe");
	result = RegSetValueEx(key, "DB", 0, REG_SZ, (BYTE*)path, strlen(path));
	if (result != ERROR_SUCCESS)
		return false;

	RegCloseKey(key);
	return true;
}
