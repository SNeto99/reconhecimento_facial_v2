#pragma once


// Tab_Other dialog

class Tab_Other : public CDialogEx
{
	DECLARE_DYNAMIC(Tab_Other)

public:
	Tab_Other(CWnd* pParent = NULL);   // standard constructor
	virtual ~Tab_Other();

// Dialog Data
	enum { IDD = IDD_TAB_OTHER };

	CWnd* pParent;

	virtual BOOL Create(UINT nIDTemplate, CWnd* pParentWnd, CWnd* pParent);

	int SetMotionDetection(char *value);
	int GetMotionDetection(char *value, int *len);

	int SetPalmSettings(char *value);
	int GetPalmSettings(char *value, int *len);

protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

	DECLARE_MESSAGE_MAP()
};
