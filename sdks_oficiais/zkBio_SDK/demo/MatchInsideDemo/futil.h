#ifndef __FUTILS_H__
#define __FUTILS_H__
#ifdef WIN32
#include <windows.h>
#else
#include <sys/time.h>
#include <stdarg.h>
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <string>
#ifndef WIN32
#include "bmp.h"
#endif
#include<iostream>
#include <vector>
#include <sstream>
#include <string>
#include <iostream>

#ifndef WIN32
DWORD GetTickCount(void);
#endif

int WriteBitmap(BYTE *buffer, int Width, int Height, char *file);

BYTE *LoadFile(const char *FileName, int *len);

int SaveToFile(const char *fileName, void *buffer, int size);

int ReadBitmap(BYTE *p, BYTE *buffer, int *Width, int *Height);

int LoadBitmapFile(const char *FileName, BYTE *buffer, int *Width, int *Height);

int AppendToFile(const char *fileName, void *buffer, int size);

int UnicodeToMultiByte(wchar_t *src, int srcLen, char *dst, int *dstLen);

int MultiByteToUnicode(char *src, int srcLen, wchar_t *dst, int *dstLen);

std::string WString2String(const std::wstring& ws);
std::wstring String2WString(const std::string& s);
std::vector<std::wstring> split_wstring(std::wstring str, wchar_t delimeter);
bool find_wstring(std::wstring str, std::wstring sfind);
std::vector<std::string> split_string(std::string str, char delimeter);
bool find_string(std::string str, std::string sfind);

int jpeg2bgr(const BYTE* pJpgData, int nSize, BYTE* bgr_buffer, int* nDatalen, int* width, int* height);

void CreateStretchImage(CImage *pImage, CImage *ResultImage, int StretchWidth, int StretchHeight);

bool save_img(const CImage &image, unsigned char *buf, int *bufSize);
bool load_img(unsigned char *buf, int len, CImage &image);

void getCurrentTime(char *timeStr);

void ReadIniInt(CString app, CString key, int &val, int defval = 0);
void ReadIniFloat(CString app, CString key, float &val, float defval = 0.0f);
void ReadIniString(CString app, CString key, CString &str, CString defstr = TEXT(""));
void WriteIniInt(CString app, CString key, int val);
void WriteIniFloat(CString app, CString key, float val);
void WriteIniString(CString app, CString key, CString str);

#endif
