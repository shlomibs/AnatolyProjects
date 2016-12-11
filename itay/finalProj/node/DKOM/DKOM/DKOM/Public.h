/*++

Module Name:

    public.h

Abstract:

    This module contains the common declarations shared by driver
    and user applications.

Environment:

    user and kernel

--*/

//
// Define an Interface Guid so that app can find the device and talk to it.
//

DEFINE_GUID (GUID_DEVINTERFACE_DKOM,
    0x7c7ba188,0xb790,0x4e19,0xb0,0x21,0xfa,0x31,0xb7,0x13,0xdf,0x16);
// {7c7ba188-b790-4e19-b021-fa31b713df16}
