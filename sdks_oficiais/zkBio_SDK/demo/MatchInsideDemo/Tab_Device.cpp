// Tab_Device.cpp : implementation file
//

#include "stdafx.h"
#include "ZKCameraDemo.h"
#include "Tab_Device.h"
#include "afxdialogex.h"
#include "futil.h"
#include "SettingDlg.h"
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include "base64.h"
#include "common.h"

using namespace rapidjson;
using namespace std;

Tab_Device* gDlg = NULL;
// Tab_Device dialog

IMPLEMENT_DYNAMIC(Tab_Device, CDialogEx)

Tab_Device::Tab_Device(CWnd* pParent /*=NULL*/)
	: CDialogEx(Tab_Device::IDD, pParent)
{
	m_bUpgradeRun = false;
	m_bSendFile = false;
}

Tab_Device::~Tab_Device()
{
}

void Tab_Device::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}


BEGIN_MESSAGE_MAP(Tab_Device, CDialogEx)
	ON_BN_CLICKED(IDC_BTN_UPGD_FIRMWARE, &Tab_Device::OnBnClickedBtnUpgdFirmware)
	ON_BN_CLICKED(IDC_BTN_UPGD_IMG, &Tab_Device::OnBnClickedBtnUpgdImg)
	ON_BN_CLICKED(IDC_BTN_UPGD_REBOOT, &Tab_Device::OnBnClickedBtnUpgdReboot)
	ON_BN_CLICKED(IDC_BTN_SYNCTIME, &Tab_Device::OnBnClickedBtnSynctime)
	ON_BN_CLICKED(IDC_BTN_GET_TIME, &Tab_Device::OnBnClickedBtnGetTime)
END_MESSAGE_MAP()


// Tab_Device message handlers
BOOL Tab_Device::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// TODO: 在此添加额外的初始化代码
	m_progress = (CProgressCtrl *)GetDlgItem(IDC_PROGRESS_UPGD);
	m_progress->SetRange(0, 100);
	m_progress->SetPos(0);

	gDlg = this;

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

BOOL Tab_Device::Create(UINT nIDTemplate, CWnd* pParentWnd, CWnd* pParent)
{
	CDialogEx::Create(nIDTemplate, pParentWnd);

	this->pParent = pParent;

	//((CSettingDlg *)pParent)->OnBnClickedBtnGet();

	return TRUE;
}

int Tab_Device::SetDeviceInfo(char *value)
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	Document document;
	document.Parse(value);

	if (document.HasParseError())
	{
		dlg->ShowInfo(_T("Parse DeviceInfo json failed"));
		return -1;
	}

	const Value& detail = document["detail"];
	if(strstr(detail.GetString(), "success"))
	{
		const Value& data = document["data"];
		string str;
		wstring wstr;

		if(!data.HasMember("deviceInfo"))
		{
			dlg->ShowInfo(_T("No deviceInfo item"));
			return -2;
		}

		const Value& deviceInfo = data["deviceInfo"];

		if(deviceInfo.HasMember("gSDK_VERSION"))
		{
			str = deviceInfo["gSDK_VERSION"].GetString();
			wstr = String2WString(str);
			SetDlgItemText(IDC_EDIT_SDKVER, wstr.c_str());
		}

		if(deviceInfo.HasMember("app"))
		{
			str = deviceInfo["app"].GetString();
			wstr = String2WString(str);
			SetDlgItemText(IDC_EDIT_APP, wstr.c_str());
		}

		if(deviceInfo.HasMember("sn"))
		{
			str = deviceInfo["sn"].GetString();
			wstr = String2WString(str);
			SetDlgItemText(IDC_EDIT_SN, wstr.c_str());
		}

		if(deviceInfo.HasMember("hidVer"))
		{
			str = deviceInfo["hidVer"].GetString();
			wstr = String2WString(str);
			SetDlgItemText(IDC_EDIT_HIDVER, wstr.c_str());
		}

		if(deviceInfo.HasMember("firmVer"))
		{
			str = deviceInfo["firmVer"].GetString();
			wstr = String2WString(str);
			SetDlgItemText(IDC_EDIT_FWVER, wstr.c_str());
		}

		if(deviceInfo.HasMember("cpID"))
		{
			str = deviceInfo["cpID"].GetString();
			wstr = String2WString(str);
			SetDlgItemText(IDC_EDIT_CHIPID, wstr.c_str());
		}
	}

	return 0;
}

void Tab_Device::OnBnClickedBtnUpgdFirmware()
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	HANDLE handle = dlg->GetHidHandle();
	if(NULL == handle)
	{
		SetDlgItemText(IDC_STATIC_HINT, _T("Please open HID first"));
		return;
	}

	if(!m_bSendFile)
	{
		m_bSendFile = true;
		m_hSendFileHandle = CreateThread(NULL, 0,                      // use default stack size  
		SendFileThread,       // thread function name
		this,          // argument to thread function 
		0,                      // use default creation flags 
		NULL);   // returns the thread identifier
	}
}

void Tab_Device::OnBnClickedBtnUpgdImg()
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	HANDLE handle = dlg->GetHidHandle();
	if(NULL == handle)
	{
		SetDlgItemText(IDC_STATIC_HINT, _T("Please open HID first"));
		return;
	}

	if(!m_bUpgradeRun)
	{
		m_bUpgradeRun = true;
		m_hUpgradeHandle = CreateThread(NULL, 0,                      // use default stack size  
		UpgradeThread,       // thread function name
		this,          // argument to thread function 
		0,                      // use default creation flags 
		NULL);   // returns the thread identifier
	}
}

void __stdcall Tab_Device::onSendFileCallback(void *pUserParam, int progress)
{
	CProgressCtrl *m_progress = (CProgressCtrl *)gDlg->GetDlgItem(IDC_PROGRESS_UPGD);

	m_progress->SetPos(progress);
}

DWORD WINAPI Tab_Device::UpgradeThread(LPVOID lpParam)
{
	Tab_Device* dlg = (Tab_Device*)lpParam;
	CSettingDlg *parent = (CSettingDlg *)dlg->pParent;
	HANDLE handle = parent->GetHidHandle();
	int ret = 0, nTick = 0;
	bool bFinishedSendFile = false;
	char filename[MAX_PATH] = {0};

	CFileDialog fileDlg(TRUE, L"", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, L"img(*.img)|*.img||"); 
	if(fileDlg.DoModal() == IDOK)
	{
		int size = 0, len = 0, ret = 0, w = 0, h = 0;
		len = MAX_PATH;
		UnicodeToMultiByte(fileDlg.GetPathName().GetBuffer(), wcslen(fileDlg.GetPathName().GetBuffer()), filename, &len);
	}
	else
	{
		goto FAIL;
	}

	nTick = GetTickCount();
	parent->ResetUSBStatus();
	ret = ZKHID_Reboot(handle, 1);
	/*if(0 != ret)
	{
		parent->ShowInfo(_T("Reboot failed"));
		goto FAIL;
	}*/
	parent->SetDeviceMode(true);

	while(dlg->m_bUpgradeRun)
	{
		Sleep(10);

		if(!parent->GetUSBStatus())
		{
			parent->ShowInfo(_T("Rebooting device..."));
			continue;
		}

		handle = parent->GetHidHandle();
		if(NULL == handle)
		{
			parent->ShowInfo(_T("Reconnecting device..."));
			continue;
		}

		parent->ResetUSBStatus();
		
		if(!bFinishedSendFile)
		{
			parent->ShowInfo(_T("SendFile..."));
			
			ret = ZKHID_SendFile(handle, UPGRADE_IMAGE, filename, onSendFileCallback, NULL);
			if(0 == ret)
			{
				parent->SetDeviceMode(false);
				parent->ShowInfo(_T("SendFile successfully, please wait the device reboot..."));
				bFinishedSendFile = true;
			}
			else
			{
				parent->ShowInfo(_T("SendFile failed"));
				break;
			}
		}
		else
		{
			wchar_t log[128] = {0};
			wsprintf(log, _T("Upgrade image successfully, time=%dms"), GetTickCount()-nTick);
			parent->ShowInfo(log);
			dlg->onSendFileCallback(NULL, 0);
			break;
		}
	}

FAIL:
	dlg->m_bUpgradeRun = false;
	CloseHandle(dlg->m_hUpgradeHandle);
	dlg->m_hUpgradeHandle = NULL;
	return 0;
}

DWORD WINAPI Tab_Device::SendFileThread(LPVOID lpParam)
{
	Tab_Device* dlg = (Tab_Device*)lpParam;
	CSettingDlg *parent = (CSettingDlg *)dlg->pParent;
	HANDLE handle = parent->GetHidHandle();
	int ret = 0, nTick = 0;
	bool bFinishedSendFile = false, bSendFirmware = false;
	char filename[MAX_PATH] = {0};
	wchar_t log[128] = {0};

	CFileDialog fileDlg(TRUE, L"", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, L"All Files(*)||"); 
	if(fileDlg.DoModal() == IDOK)
	{
		int size = 0, len = 0, ret = 0, w = 0, h = 0;
		len = MAX_PATH;
		UnicodeToMultiByte(fileDlg.GetPathName().GetBuffer(), wcslen(fileDlg.GetPathName().GetBuffer()), filename, &len);
		char *fname = PathFindFileNameA(filename);
		if(0 == stricmp(fname, "ZKfirmware.tar"))
		{
			bSendFirmware = true;
		}
	}
	else
	{
		goto FAIL;
	}

	nTick = GetTickCount();

	while(dlg->m_bSendFile)
	{
		Sleep(10);

		if(bFinishedSendFile && bSendFirmware)
		{
			if(!parent->GetUSBStatus())
			{
				parent->ShowInfo(_T("Rebooting device..."));
				continue;
			}

			handle = parent->GetHidHandle();
			if(NULL == handle)
			{
				parent->ShowInfo(_T("Reconnecting device..."));
				continue;
			}

			parent->ResetUSBStatus();
		}

		if(!bFinishedSendFile)
		{
			parent->ShowInfo(_T("SendFile..."));
			
			ret = ZKHID_SendFile(handle, SEND_FILE, filename, onSendFileCallback, NULL);
			if(0 == ret)
			{
				bFinishedSendFile = true;
				if(!bSendFirmware)
				{
					wsprintf(log, _T("SendFile successfully, time=%dms"), GetTickCount()-nTick);
					parent->ShowInfo(log);
					dlg->onSendFileCallback(NULL, 0);
					break;
				}
				parent->ShowInfo(_T("SendFile successfully, please wait the device reboot..."));
				
			}
			else
			{
				parent->ShowInfo(_T("SendFile failed"));
				break;
			}
		}
		else
		{
			wsprintf(log, _T("Upgrade Firmware successfully, time=%dms"), GetTickCount()-nTick);
			parent->ShowInfo(log);
			dlg->onSendFileCallback(NULL, 0);
			break;
		}
	}

FAIL:
	dlg->m_bSendFile = false;
	CloseHandle(dlg->m_hSendFileHandle);
	dlg->m_hSendFileHandle = NULL;
	return 0;
}

void Tab_Device::OnBnClickedBtnUpgdReboot()
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	HANDLE handle = dlg->GetHidHandle();
	if(NULL == handle)
	{
		SetDlgItemText(IDC_STATIC_HINT, _T("Please open HID first"));
		return;
	}

	int ret = ZKHID_Reboot(handle, 0);
	if(0 == ret)
	{
		dlg->ShowInfo(_T("Reboot successfully"));
	}
	else
	{
		dlg->ShowInfo(_T("Reboot failed"));
	}
}

void Tab_Device::OnBnClickedBtnSynctime()
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	HANDLE handle = dlg->GetHidHandle();
	if(NULL == handle)
	{
		dlg->ShowInfo(_T("Please open HID first"));
		return;
	}

	wchar_t wc[64] = {0};
	char timeStr[64] = {0};
	SYSTEMTIME stLocal;
	GetLocalTime(&stLocal);
	sprintf(timeStr, "%d-%02d-%02d %02d:%02d:%02d", stLocal.wYear, stLocal.wMonth, stLocal.wDay, stLocal.wHour, stLocal.wMinute, stLocal.wSecond);
	string json = getSyncTimeJson(timeStr);
	int ret = ZKHID_SetConfig(handle, DEVICE_TIME, (char *)json.c_str());
	if(0 == ret)
	{
		dlg->ShowInfo(_T("Sync time successfully"));
	}
	else
	{
		wsprintf(wc, L"Sync time failed, ret=%d", ret);
		dlg->ShowInfo(wc);
	}
}

void Tab_Device::OnBnClickedBtnGetTime()
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	HANDLE handle = dlg->GetHidHandle();
	if(NULL == handle)
	{
		dlg->ShowInfo(_T("Please open HID first"));
		return;
	}

	wchar_t wc[64] = {0};
	char json[1024] = {0};
	int len = 1024;
	int ret = ZKHID_GetConfig(handle, DEVICE_TIME, json, &len);
	if(0 == ret)
	{
		int status = 0;
		string detail, sysTime;
		ret = parseDeviceTime(json, &status, detail, sysTime);
		if(0 == ret)
		{
			SetDlgItemText(IDC_EDIT_TIME, String2WString(sysTime).c_str());
		}
		else
		{
			wsprintf(wc, L"Get time failed, ret=%d, status=%d", ret, status);
			dlg->ShowInfo(wc);
		}
	}
	else
	{
		wsprintf(wc, L"Get time failed, ret=%d", ret);
		dlg->ShowInfo(wc);
	}
}
