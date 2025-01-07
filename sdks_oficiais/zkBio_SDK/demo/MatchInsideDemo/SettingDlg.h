#pragma once
#include "afxcmn.h"
#include "Tab_Device.h"
#include "Tab_Param.h"
#include "Tab_Other.h"
#include "ZKHIDLib.h"

// CSettingDlg dialog
using namespace std;

class CSettingDlg : public CDialogEx
{
	DECLARE_DYNAMIC(CSettingDlg)

private:
	
public:
	CSettingDlg(CWnd* pParent = NULL);   // standard constructor
	virtual ~CSettingDlg();

// Dialog Data
	enum { IDD = IDD_SETTING_DIALOG };

	Tab_Device tab_device;
	Tab_Param tab_param;
	Tab_Other tab_other;

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	virtual BOOL OnInitDialog();

	DECLARE_MESSAGE_MAP()

	virtual BOOL PreTranslateMessage(MSG* pMsg);
public:
	CTabCtrl m_tab;
	afx_msg void OnTcnSelchangeTab1(NMHDR *pNMHDR, LRESULT *pResult);

	afx_msg void OnBnClickedBtnGet();
	afx_msg void OnBnClickedBtnSet(); 

	void ShowInfo(wstring wstr);

	HANDLE GetHidHandle();
	bool GetUSBStatus();
	void ResetUSBStatus();
	void SetFaceThreshold(float threshold);
	void SetPalmThreshold(int threshold);
	void SetDeviceMode(bool bUpgradeImage);
};
