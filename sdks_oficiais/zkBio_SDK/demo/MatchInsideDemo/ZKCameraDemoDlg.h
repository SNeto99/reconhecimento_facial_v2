
// ZKCameraDemoDlg.h : header file
//

#pragma once

#include "SettingDlg.h"
#include "common.h"

#define WM_DEVICEATTACH WM_USER + 12

// CZKCameraDemoDlg dialog
class CZKCameraDemoDlg : public CDialogEx
{
// Construction
public:
	CZKCameraDemoDlg(CWnd* pParent = NULL);	// standard constructor

// Dialog Data
	enum { IDD = IDD_ZKCAMERADEMO_DIALOG };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV support


// Implementation
protected:
	HICON m_hIcon;

	// Generated message map functions
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()

	virtual BOOL PreTranslateMessage(MSG* pMsg);

	static DWORD WINAPI ViewThread(LPVOID lpParam);
	static DWORD WINAPI NIRViewThread(LPVOID lpParam);
	static DWORD WINAPI MatchThread(LPVOID lpParam);
	static DWORD WINAPI RegFaceThread(LPVOID lpParam);
	static DWORD WINAPI RegPalmThread(LPVOID lpParam);
	static DWORD WINAPI PollHIDStatusThread(LPVOID lpParam);

private:
	bool bRegPalm;
	HANDLE m_hViewHandle;
	HANDLE m_hNIRViewHandle;
	HANDLE m_hMatchHandle;
	HANDLE m_hRegPalmHandle;
	HANDLE m_hRegFaceHandle;
	HANDLE m_hPollHIDHandle;
	bool m_bViewRun;
	bool m_bMatchRun;
	bool m_bRegPalmRun;
	bool m_bRegFaceRun;
	bool m_bPollHIDRun;
	unsigned char *bgr;
	unsigned char *nirImage;

	CSettingDlg settingDlg;

	HDEVNOTIFY mNotifyDevHandle;
	HDEVNOTIFY mNotifyHubHandle;
public:
	CStatusBarCtrl     *mStatusBar;

	afx_msg void OnBnClickedBtnOpen();
	afx_msg void OnBnClickedBtnClose();
	afx_msg void OnClose();

	void updateView(unsigned char* mjpeg, int w, int h);
	void updateNIRView(unsigned char* mjpeg, int w, int h);
	afx_msg void OnBnClickedBtnOpenHid();
	afx_msg void OnBnClickedBtnCloseHid();
	afx_msg void OnBnClickedBtnReg();
	afx_msg void OnBnClickedBtnDevicemanage();
	static BioRect* GetBioRect(CustomBioData customBioData);

	HANDLE GetHidHandle();
	bool GetUSBStatus();
	void ResetUSBStatus();
	void SetFaceThreshold(float threshold);
	void SetPalmThreshold(int threshold);
	void SetDeviceMode(bool bUpgradeImage);
	afx_msg void OnBnClickedBtnSnapshot();
	afx_msg void OnBnClickedBtnClear();

	int KillThread(HANDLE &thread);
	afx_msg void OnBnClickedBtnLocalregpalm();

	afx_msg void OnBnClickedBtnDeluser();
	afx_msg void OnBnClickedBtnHidtest();

	afx_msg BOOL OnDeviceChange(UINT nEventType, DWORD_PTR dwData);
	afx_msg LRESULT OnDeviceAttach(WPARAM wParam,LPARAM lParam);
	afx_msg void OnBnClickedBtnAdduser();
	afx_msg void OnBnClickedBtnGetalluser();

	int ManageUser(int manageType, char *json);
	afx_msg void OnBnClickedBtnRegfromfile();
	afx_msg void OnBnClickedBtnGetuser();
	afx_msg void OnSize(UINT nType, int cx, int cy);
	afx_msg void OnTimer(UINT_PTR nIDEvent);
	afx_msg void OnBnClickedCheckPollmatchresult();
	afx_msg void OnBnClickedBtnClearAttRecord();
	afx_msg void OnBnClickedBtnGetAttRecord();

	void EnableControl(bool bEnable);
};
