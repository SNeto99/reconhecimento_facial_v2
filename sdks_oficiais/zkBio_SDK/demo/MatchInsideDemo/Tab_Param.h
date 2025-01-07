#pragma once


// Tab_Param dialog

class Tab_Param : public CDialogEx
{
	DECLARE_DYNAMIC(Tab_Param)

public:
	Tab_Param(CWnd* pParent = NULL);   // standard constructor
	virtual ~Tab_Param();

// Dialog Data
	enum { IDD = IDD_TAB_PARAM };

	CWnd* pParent;

	virtual BOOL Create(UINT nIDTemplate, CWnd* pParentWnd, CWnd* pParent);

	void OnEnChangeEdit(UINT nID);

	int SetCommonSettings(char *value);
	int GetCommonSettings(char *value, int *len);

	int SetCaptureFilter(char *value);
	int GetCaptureFilter(char *value, int *len);

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()

	virtual BOOL OnInitDialog();
public:
	afx_msg void OnDeltaposSpinDebug(NMHDR *pNMHDR, LRESULT *pResult);
	afx_msg void OnHScroll(UINT nSBCode, UINT nPos, CScrollBar* pScrollBar);
};
