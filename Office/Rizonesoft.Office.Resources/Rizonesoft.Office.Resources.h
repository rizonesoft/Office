// Rizonesoft.Office.Resources.h : main header file for the Rizonesoft.Office.Resources DLL
//

#pragma once

#ifndef __AFXWIN_H__
	#error "include 'pch.h' before including this file for PCH"
#endif

#include "resource.h"		// main symbols


// CRizonesoftOfficeResourcesApp
// See Rizonesoft.Office.Resources.cpp for the implementation of this class
//

class CRizonesoftOfficeResourcesApp : public CWinApp
{
public:
	CRizonesoftOfficeResourcesApp();

// Overrides
public:
	virtual BOOL InitInstance();

	DECLARE_MESSAGE_MAP()
};
