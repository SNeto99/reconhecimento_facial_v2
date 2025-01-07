#pragma once


// Tab_Device dialog

class Tab_Device : public CDialogEx
{
	DECLARE_DYNAMIC(Tab_Device)

public:
	Tab_Device(CWnd* pParent = NULL);   // standard constructor
	virtual ~Tab_Device();

// Dialog Data
	enum { IDD = IDD_TAB_DEVICE };

	CWnd* pParent;
	bool m_bUpgradeRun;
	bool m_bSendFile;
	HANDLE m_hUpgradeHandle;
	HANDLE m_hSendFileHandle;
	CProgressCtrl *m_progress;

	virtual BOOL Create(UINT nIDTemplate, CWnd* pParentWnd, CWnd* pParent);

	int SetDeviceInfo(char *value);

	static DWORD WINAPI UpgradeThread(LPVOID lpParam);

	static DWORD WINAPI SendFileThread(LPVOID lpParam);

	static void __stdcall onSendFileCallback(void *pUserParam, int progress);

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	virtual BOOL OnInitDialog();

	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedBtnUpgdFirmware();
	afx_msg void OnBnClickedBtnUpgdImg();

	afx_msg void OnBnClickedBtnUpgdReboot();
	afx_msg void OnBnClickedBtnSynctime();
	afx_msg void OnBnClickedBtnGetTime();
};
