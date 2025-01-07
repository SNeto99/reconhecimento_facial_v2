// SettingDlg.cpp : implementation file
//

#include "stdafx.h"
#include "ZKCameraDemo.h"
#include "SettingDlg.h"
#include "afxdialogex.h"
#include "futil.h"
#include "ZKCameraDemoDlg.h"
#include "rapidjson/document.h"

using namespace rapidjson;
using namespace std;

// CSettingDlg dialog

IMPLEMENT_DYNAMIC(CSettingDlg, CDialogEx)

CSettingDlg::CSettingDlg(CWnd* pParent /*=NULL*/)
	: CDialogEx(CSettingDlg::IDD, pParent)
{
	
}

CSettingDlg::~CSettingDlg()
{
}

void CSettingDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Control(pDX, IDC_TAB1, m_tab);
}


BEGIN_MESSAGE_MAP(CSettingDlg, CDialogEx)
	ON_NOTIFY(TCN_SELCHANGE, IDC_TAB1, &CSettingDlg::OnTcnSelchangeTab1)
	ON_BN_CLICKED(IDC_BTN_GET, &CSettingDlg::OnBnClickedBtnGet)
	ON_BN_CLICKED(IDC_BTN_SET, &CSettingDlg::OnBnClickedBtnSet)
END_MESSAGE_MAP()


// CSettingDlg message handlers
BOOL CSettingDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// Add "About..." menu item to system menu.
	m_tab.InsertItem(0, _T("Device"));
	m_tab.InsertItem(1, _T("Face Parameter"));
	m_tab.InsertItem(2, _T("Other"));

	tab_device.Create(IDD_TAB_DEVICE, GetDlgItem(IDC_TAB1), this);
	tab_param.Create(IDD_TAB_PARAM, GetDlgItem(IDC_TAB1), this);
	tab_other.Create(IDD_TAB_OTHER, GetDlgItem(IDC_TAB1), this);

	CRect rect;    
	m_tab.GetClientRect(&rect);   
	rect.top += 20;   
	rect.bottom -= 4;   
	rect.left += 4;  
	rect.right -= 4;   

	tab_device.MoveWindow(&rect); 
	tab_param.MoveWindow(&rect); 
	tab_other.MoveWindow(&rect); 
	tab_device.ShowWindow(TRUE);   
	m_tab.SetCurSel(0);
	GetDlgItem(IDC_BTN_SET)->EnableWindow(FALSE);

	return TRUE;  // return TRUE  unless you set the focus to a control
}

BOOL CSettingDlg::PreTranslateMessage(MSG* pMsg)
{
    if(pMsg->message==WM_KEYDOWN && (pMsg->wParam==VK_ESCAPE || pMsg->wParam==VK_RETURN))
        return TRUE;
    else
        return CDialog::PreTranslateMessage(pMsg);
}

void CSettingDlg::OnTcnSelchangeTab1(NMHDR *pNMHDR, LRESULT *pResult)
{
	CRect rect;  // 标签控件客户区的Rect  
	// 获取标签控件客户区Rect，并对其调整，以适合放置标签页
	m_tab.GetClientRect(&rect); 
	rect.top += 20;   
	rect.bottom -= 4;   
	rect.left += 4;  
	rect.right -= 4; 

    switch (m_tab.GetCurSel())   
    {   
    // 如果标签控件当前选择标签为“校正参数”，则显示m_Tab0对话框，隐藏其他对话框   
    case 0:   
        tab_device.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_SHOWWINDOW);   
        tab_param.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_HIDEWINDOW); 
		tab_other.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_HIDEWINDOW);
		GetDlgItem(IDC_BTN_SET)->EnableWindow(FALSE);
        break;
	 case 1:   
        tab_device.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_HIDEWINDOW);   
        tab_param.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_SHOWWINDOW); 
		tab_other.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_HIDEWINDOW);
		GetDlgItem(IDC_BTN_SET)->EnableWindow(TRUE);
        break;
	 case 2:   
        tab_device.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_HIDEWINDOW);   
        tab_param.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_HIDEWINDOW); 
		tab_other.SetWindowPos(NULL, rect.left, rect.top, rect.Width(), rect.Height(), SWP_SHOWWINDOW);
		GetDlgItem(IDC_BTN_SET)->EnableWindow(TRUE);
        break;
	 default:
		 break;
	}

	*pResult = 0;
}

void CSettingDlg::OnBnClickedBtnGet()
{
	HANDLE handle = GetHidHandle();
	if(NULL == handle)
	{
		SetDlgItemText(IDC_STATIC_HINT, _T("Please open HID first"));
		return;
	}
	wchar_t log[128] = {0};
	switch (m_tab.GetCurSel())
	{
	case 0:
		{
			int len = 1024;
			int ret = 0;
			char *json = (char *)malloc(len);
			ret = ZKHID_GetConfig(handle, DEVICE_INFORMATION, json, &len);
			if(0 == ret)
			{
				SetDlgItemText(IDC_STATIC_HINT, _T("GetConfig successfully"));
				tab_device.SetDeviceInfo(json);
			}
			else
			{
				wsprintf(log, _T("GetConfig failed, ret=%d"), ret);
				SetDlgItemText(IDC_STATIC_HINT, log);
			}
		}
		break;
	case 1:
		{
			int len = 1024;
			int ret = 0;
			char *json = (char *)malloc(len);
			ret = ZKHID_GetConfig(handle, COMMON_CONFIG, json, &len);
			if(0 == ret)
			{
				SetDlgItemText(IDC_STATIC_HINT, _T("GetConfig successfully"));
				tab_param.SetCommonSettings(json);
			}
			else
			{
				wsprintf(log, _T("GetConfig failed, ret=%d"), ret);
				SetDlgItemText(IDC_STATIC_HINT, log);
			}

			len = 1024;
			ret = ZKHID_GetConfig(handle, CAPTURE_FILTER_CONFIG, json, &len);
			if(0 == ret)
			{
				SetDlgItemText(IDC_STATIC_HINT, _T("GetConfig successfully"));
				tab_param.SetCaptureFilter(json);
			}
			else
			{
				wsprintf(log, _T("GetConfig failed, ret=%d"), ret);
				SetDlgItemText(IDC_STATIC_HINT, log);
			}
		}
		break;
	case 2:
		{
			int len = 1024;
			int ret = 0;
			char *json = (char *)malloc(len);
			ret = ZKHID_GetConfig(handle, MOTION_DETECT_CONFIG, json, &len);
			if(0 == ret)
			{
				SetDlgItemText(IDC_STATIC_HINT, _T("GetConfig successfully"));
				tab_other.SetMotionDetection(json);
			}
			else
			{
				wsprintf(log, _T("GetConfig failed, ret=%d"), ret);
				SetDlgItemText(IDC_STATIC_HINT, log);
			}

			len = 1024;
			ret = ZKHID_GetConfig(handle, PALM_CONFIG, json, &len);
			if(0 == ret)
			{
				SetDlgItemText(IDC_STATIC_HINT, _T("GetConfig successfully"));
				tab_other.SetPalmSettings(json);
			}
			else
			{
				wsprintf(log, _T("GetConfig failed, ret=%d"), ret);
				SetDlgItemText(IDC_STATIC_HINT, log);
			}
		}
		break;
	default:
		break;
	}
}


void CSettingDlg::OnBnClickedBtnSet()
{
	HANDLE handle = GetHidHandle();
	if(NULL == handle)
	{
		SetDlgItemText(IDC_STATIC_HINT, _T("Please open HID first"));
		return;
	}
	wchar_t wc[64] = {0};
	switch (m_tab.GetCurSel())
	{
	case 1:
		{
			int len = 1024;
			int ret = 0;
			char *json = (char *)malloc(len);

			ret = tab_param.GetCommonSettings(json, &len);
			if(0 == ret)
			{
				ret = ZKHID_SetConfig(handle, COMMON_CONFIG, json);
				if(0 == ret)
				{
					SetDlgItemText(IDC_STATIC_HINT, _T("SetConfig successfully"));
				}
				else
				{
					wsprintf(wc, L"SetConfig failed, ret=%d", ret);
					SetDlgItemText(IDC_STATIC_HINT, wc);
				}
			}
			else
			{
				wsprintf(wc, L"GetCommonSettings failed, ret=%d", ret);
				SetDlgItemText(IDC_STATIC_HINT, wc);
			}

			len = 1024;
			ret = tab_param.GetCaptureFilter(json, &len);
			if(0 == ret)
			{
				ret = ZKHID_SetConfig(handle, CAPTURE_FILTER_CONFIG, json);
				if(0 == ret)
				{
					SetDlgItemText(IDC_STATIC_HINT, _T("SetConfig successfully"));
				}
				else
				{
					wsprintf(wc, L"SetConfig failed, ret=%d", ret);
					SetDlgItemText(IDC_STATIC_HINT, wc);
				}
			}
			else
			{
				wsprintf(wc, L"GetCaptureFilter failed, ret=%d", ret);
				SetDlgItemText(IDC_STATIC_HINT, wc);
			}
		}
		break;
	case 2:
		{
			int len = 1024;
			int ret = 0;
			char *json = (char *)malloc(len);

			ret = tab_other.GetMotionDetection(json, &len);
			if(0 == ret)
			{
				ret = ZKHID_SetConfig(handle, MOTION_DETECT_CONFIG, json);
				if(0 == ret)
				{
					SetDlgItemText(IDC_STATIC_HINT, _T("SetConfig successfully"));
				}
				else
				{
					wsprintf(wc, L"SetConfig failed, ret=%d", ret);
					SetDlgItemText(IDC_STATIC_HINT, wc);
				}
			}
			else
			{
				wsprintf(wc, L"GetMotionDetection failed, ret=%d", ret);
				SetDlgItemText(IDC_STATIC_HINT, wc);
			}

			len = 1024;
			ret = tab_other.GetPalmSettings(json, &len);
			if(0 == ret)
			{
				ret = ZKHID_SetConfig(handle, PALM_CONFIG, json);
				if(0 == ret)
				{
					SetDlgItemText(IDC_STATIC_HINT, _T("SetConfig successfully"));
				}
				else
				{
					wsprintf(wc, L"SetConfig failed, ret=%d", ret);
					SetDlgItemText(IDC_STATIC_HINT, wc);
				}
			}
			else
			{
				wsprintf(wc, L"GetPalmSettings failed, ret=%d", ret);
				SetDlgItemText(IDC_STATIC_HINT, wc);
			}
		}
		break;
	default:
		break;
	}

	OnBnClickedBtnGet();
}

void CSettingDlg::ShowInfo(wstring wstr)
{
	SetDlgItemText(IDC_STATIC_HINT, wstr.c_str());
}

HANDLE CSettingDlg::GetHidHandle()
{
	return ((CZKCameraDemoDlg *)GetParent())->GetHidHandle();
}

bool CSettingDlg::GetUSBStatus()
{
	return ((CZKCameraDemoDlg *)GetParent())->GetUSBStatus();
}

void CSettingDlg::ResetUSBStatus()
{
	return ((CZKCameraDemoDlg *)GetParent())->ResetUSBStatus();
}

void CSettingDlg::SetFaceThreshold(float threshold)
{
	return ((CZKCameraDemoDlg *)GetParent())->SetFaceThreshold(threshold);
}

void CSettingDlg::SetPalmThreshold(int threshold)
{
	return ((CZKCameraDemoDlg *)GetParent())->SetPalmThreshold(threshold);
}

void CSettingDlg::SetDeviceMode(bool bUpgradeImage)
{
	return ((CZKCameraDemoDlg *)GetParent())->SetDeviceMode(bUpgradeImage);
}