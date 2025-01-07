#include "stdafx.h"
#include "futil.h"
#include "libjpeg/jpeglib.h"
#include "libjpeg/jerror.h"
#include <setjmp.h>
#ifdef _WIN64
#pragma comment(lib, "libjpeg/libjpeg_x64.lib")
#else
#pragma comment(lib, "libjpeg/libjpeg_x86.lib")
#endif

using namespace std;

#ifndef WIN32
DWORD GetTickCount(void)
{
	struct timeval tv;
	struct timezone tz;
	gettimeofday(&tv, &tz);
	return (tv.tv_sec*1000 + tv.tv_usec/1000);
}
#endif

int WriteBitmap(BYTE *buffer, int Width, int Height, char *file)
{
	char Buffer[0x500];
	BITMAPFILEHEADER *bmpfheader=(BITMAPFILEHEADER *)Buffer;
	BITMAPINFO *bmpinfo=(BITMAPINFO *)(((char*)bmpfheader)+14);
	int i,w;
	FILE *f;
	memset(bmpfheader,0,0x500);
	bmpfheader->bfType =19778;
	w = ((Width+3)/4)*4*Height+sizeof(BITMAPFILEHEADER)+sizeof(BITMAPINFO)+255*sizeof(RGBQUAD);
	memcpy((void*)(((char*)bmpfheader)+2), &w, 4);
	//bmpfheader->bfOffBits;
	w= sizeof(BITMAPFILEHEADER)+sizeof(BITMAPINFO)+255*sizeof(RGBQUAD);
	memcpy((void*)(((char*)bmpfheader)+10), &w, 4);
	bmpinfo->bmiHeader.biWidth=Width;
	bmpinfo->bmiHeader.biHeight=Height;
	bmpinfo->bmiHeader.biBitCount=8;
	bmpinfo->bmiHeader.biClrUsed=0;
	bmpinfo->bmiHeader.biSize=sizeof(bmpinfo->bmiHeader);
	bmpinfo->bmiHeader.biPlanes=1;
	bmpinfo->bmiHeader.biSizeImage=((Width+3)/4)*4*Height;
	f=fopen(file, "wb");
	if(f)
	{
		for(i=1;i<256;i++)
		{
			bmpinfo->bmiColors[i].rgbBlue=i;
			bmpinfo->bmiColors[i].rgbGreen=i;
			bmpinfo->bmiColors[i].rgbRed=i;
		}
		fwrite(Buffer, sizeof(BITMAPFILEHEADER)+sizeof(BITMAPINFOHEADER)+256*sizeof(RGBQUAD), 1, f);

		w = ((Width+3)/4)*4;
		buffer+=Width*(Height-1);
		for(i=0; i<Height; i++)
		{
			fwrite(buffer, Width, 1, f);
			if(w-Width)
				fwrite(buffer, w-Width, 1, f);
			buffer-=Width;
		}
		fclose(f);
		return Width*Height;
	}
	return 0;
}

BYTE *LoadFile(const char *FileName, int *len)
{
	BYTE *data=NULL;
	FILE *f=fopen(FileName, "rb"); 
	long s;
	if(!f)
	{
		return 0;
	}
	fseek(f,0,SEEK_END);
	s=ftell(f);
	if(s>0)
	{
		fseek(f,0,SEEK_SET);
		data=(BYTE*)malloc(s);
		if (1>(long)fread(data, s, 1, f))
		{
			free(data);
			data=NULL;
		}

		*len = s;
	}
	fclose(f);
	return data;
}

int SaveToFile(const char *fileName, void *buffer, int size)
{
	FILE *f=fopen(fileName, "wb");
	if(f==NULL)
	{
		return 0;
	}
	fwrite(buffer, size, 1, f);
	fclose(f);
	return 1;
}

int ReadBitmap(BYTE *p, BYTE *buffer, int *Width, int *Height)
{
	BITMAPFILEHEADER *bmpfheader=(BITMAPFILEHEADER *)p;
	BITMAPINFO *bmpinfo=(BITMAPINFO *)(p+14);
	int i,w;
	if(!p) return 0;

	*Width = bmpinfo->bmiHeader.biWidth;
	*Height=bmpinfo->bmiHeader.biHeight;
	if((bmpfheader->bfType ==19778) && (bmpinfo->bmiHeader.biCompression==0) &&
		(bmpinfo->bmiHeader.biBitCount==8))
	{
		if(bmpinfo->bmiHeader.biClrUsed==0) bmpinfo->bmiHeader.biClrUsed=256;
		if(bmpinfo->bmiHeader.biClrUsed!=256) return 0;
		p+=0x436;
		w = ((*Width+3)/4)*4;
		p+=w*(*Height-1);
		if(buffer)
			for(i=0; i<(int)*Height; i++)
			{
				memcpy(buffer, p, *Width);
				buffer+=*Width;
				p-=w;
			}
	}
	else
	{
		return 0;
	}
	return *Width**Height;
}

int LoadBitmapFile(const char *FileName, BYTE *buffer, int *Width, int *Height)
{
	int len = 0;
	unsigned char *p=LoadFile(FileName, &len);
	int res=ReadBitmap(p, buffer, Width, Height);
	free(p);
	return res;
}

int AppendToFile(const char *fileName, void *buffer, int size)
{
	FILE *f=fopen(fileName, "ab");
	if(f==NULL)
	{
		printf("Open file %s to write fail.\n", fileName);
		return 0;
	}
	fwrite(buffer, size, 1, f);
	fclose(f);
	return 1;
}

int UnicodeToMultiByte(wchar_t *src, int srcLen, char *dst, int *dstLen)
{
	int ret = 0;
	int bufSize = WideCharToMultiByte(CP_ACP, 0, src, srcLen, NULL, 0, 0, 0);
	char *buf = (char *)malloc(bufSize);

	WideCharToMultiByte(CP_ACP, 0, src, srcLen, buf, bufSize, 0, 0);

	if(*dstLen >= bufSize)
	{
		memcpy(dst, buf, bufSize);
		*dstLen = bufSize;
		ret = 0;
	}
	else
	{
		ret = -1;
	}

	free(buf);

	return ret;
}

int MultiByteToUnicode(char *src, int srcLen, wchar_t *dst, int *dstLen)
{
	int ret = 0;
	DWORD dBufSize = MultiByteToWideChar(CP_ACP, 0, src, srcLen, NULL, 0);

    wchar_t * dBuf = new wchar_t[dBufSize];
    wmemset(dBuf, 0, dBufSize);
	

    MultiByteToWideChar(CP_ACP, 0, src, strlen(src), dBuf, dBufSize);

	if(*dstLen >= dBufSize)
	{
		wmemcpy(dst, dBuf, dBufSize);
		*dstLen = dBufSize;
		ret = 0;
	}
	else
	{
		ret = -1;
	}

	delete []dBuf;

	return ret;
}

//wstring=>string
std::string WString2String(const std::wstring& ws)
{
    std::string strLocale = setlocale(LC_ALL, "");
    const wchar_t* wchSrc = ws.c_str();
    size_t nDestSize = wcstombs(NULL, wchSrc, 0) + 1;
    char *chDest = new char[nDestSize];
    memset(chDest, 0, nDestSize);
    wcstombs(chDest, wchSrc, nDestSize);
    std::string strResult = chDest;
    delete[]chDest;
    setlocale(LC_ALL, strLocale.c_str());
    return strResult;
}
// string => wstring
std::wstring String2WString(const std::string& s)
{
    std::string strLocale = setlocale(LC_ALL, "");
    const char* chSrc = s.c_str();
    size_t nDestSize = mbstowcs(NULL, chSrc, 0) + 1;
    wchar_t* wchDest = new wchar_t[nDestSize];
    wmemset(wchDest, 0, nDestSize);
    mbstowcs(wchDest, chSrc, nDestSize);
    std::wstring wstrResult = wchDest;
    delete[]wchDest;
    setlocale(LC_ALL, strLocale.c_str());
    return wstrResult;
}

std::vector<std::wstring> split_wstring(std::wstring str, wchar_t delimeter)
{
	std::wstring temp;
	std::vector<std::wstring> parts;
	std::wstringstream wss(str);
	while (std::getline(wss, temp, delimeter))
		parts.push_back(temp);

	return parts;
}

bool find_wstring(std::wstring str, std::wstring sfind)
{
	std::string::size_type found = str.find(sfind);
	if (found != std::string::npos)
		return true;
	return false;
}

std::vector<std::string> split_string(std::string str, char delimeter)
{
	std::string temp;
	std::vector<std::string> parts;
	std::stringstream wss(str);
	while (std::getline(wss, temp, delimeter))
		parts.push_back(temp);

	return parts;
}

bool find_string(std::string str, std::string sfind)
{
	std::string::size_type found = str.find(sfind);
	if (found != std::string::npos)
		return true;
	return false;
}

#ifdef _ZKLIBJPEG
#define ZKPRE(x) zk_##x
#else
#define ZKPRE(x) x
#endif

struct my_error_mgr
{
	struct ZKPRE(jpeg_error_mgr) pub;	/* "public" fields */
	jmp_buf setjmp_buffer;	/* for return to caller */
};

typedef struct my_error_mgr * my_error_ptr;

METHODDEF(void) my_error_exit (j_common_ptr cinfo) 
{ 
	my_error_ptr myerr = (my_error_ptr) cinfo->err; 

	(*cinfo->err->output_message) (cinfo); 

	longjmp(myerr->setjmp_buffer, 1); 
} 

int jpeg2bgr(const BYTE* pJpgData, int nSize, BYTE* bgr_buffer, int* nDatalen, int* width, int* height)
{
	struct jpeg_decompress_struct cinfo;
	struct my_error_mgr jerr;

	JSAMPARRAY buffer;
	int row_stride = 0;
	unsigned char* tmp_buffer = NULL;
	int rgb_size;

	cinfo.err = jpeg_std_error(&jerr.pub);
	jerr.pub.error_exit = my_error_exit;

	if (setjmp(jerr.setjmp_buffer))
	{
		jpeg_destroy_decompress(&cinfo);
		return -1;
	}

	jpeg_create_decompress(&cinfo);
	jpeg_mem_src(&cinfo, (BYTE*)pJpgData, nSize);   //// 指定图片在内存的地址及大小	

	jpeg_read_header(&cinfo, TRUE);
	cinfo.out_color_space = JCS_RGB; //JCS_YCbCr;  // 设置输出格式  
	jpeg_start_decompress(&cinfo);

	row_stride = cinfo.output_width * cinfo.output_components;
	*width = cinfo.output_width;
	*height = cinfo.output_height;

	rgb_size = row_stride * cinfo.output_height; // 总大小  
	if (NULL == bgr_buffer)
	{
		*nDatalen = rgb_size;
		return 0;
	}

	if (*nDatalen < rgb_size)
	{
		jpeg_finish_decompress(&cinfo);
		jpeg_destroy_decompress(&cinfo);
		return -2;
	}
	*nDatalen = rgb_size;
	buffer = (*cinfo.mem->alloc_sarray)((j_common_ptr)&cinfo, JPOOL_IMAGE, row_stride, 1);
	tmp_buffer = bgr_buffer;
	while (cinfo.output_scanline < cinfo.output_height) // 解压每一行  
	{
		jpeg_read_scanlines(&cinfo, buffer, 1); 
		memcpy(tmp_buffer, buffer[0], row_stride);
		tmp_buffer += row_stride;
	}
	unsigned char temp = 0;
	for (int i = 0; i < rgb_size / 3; i++)
	{
		temp = bgr_buffer[i * 3];
		bgr_buffer[i * 3] = bgr_buffer[i * 3 + 2];
		bgr_buffer[i * 3 + 2] = temp;
	}
	jpeg_finish_decompress(&cinfo);
	jpeg_destroy_decompress(&cinfo);
	return *nDatalen;
}

//Resize CImage
void CreateStretchImage(CImage *pImage,CImage *ResultImage, int StretchWidth, int StretchHeight)
{
	if(pImage->IsDIBSection())
	{
		CDC* pImageDC1 = CDC::FromHandle(pImage->GetDC());

		CBitmap *bitmap1 = pImageDC1->GetCurrentBitmap();
		BITMAP bmpInfo;
		bitmap1->GetBitmap(&bmpInfo);

		ResultImage->Create(StretchWidth, StretchHeight, bmpInfo.bmBitsPixel);
		CDC* ResultImageDC = CDC::FromHandle(ResultImage->GetDC());

		ResultImageDC->SetStretchBltMode(HALFTONE);
		::SetBrushOrgEx(ResultImageDC->m_hDC, 0, 0, NULL);

		StretchBlt(*ResultImageDC, 0, 0, StretchWidth, StretchHeight, *pImageDC1, 0, 0, pImage->GetWidth(), pImage->GetHeight(), SRCCOPY);

		pImage->ReleaseDC();
		ResultImage->ReleaseDC();
	}
}

bool save_img(const CImage &image, unsigned char *buf, int *bufSize) 
{
    IStream *stream = NULL;
    HRESULT hr = CreateStreamOnHGlobal(0, TRUE, &stream);
    if( !SUCCEEDED(hr) )
        return false;
    image.Save(stream, Gdiplus::ImageFormatJPEG);
    ULARGE_INTEGER liSize;
    IStream_Size(stream, &liSize);
    DWORD len = liSize.LowPart;
	if(NULL == buf)
	{
		stream->Release();
		*bufSize = len;
		return true;
	}
	if(*bufSize < len)
	{
		stream->Release();
		return false;
	}
    IStream_Reset(stream);
    IStream_Read(stream, buf, len);
	*bufSize = len;
    stream->Release();
    return true;
}

bool load_img(unsigned char *buf, int len, CImage &image)
{
    HGLOBAL hMem = GlobalAlloc(GMEM_FIXED, len);
    BYTE *pmem = (BYTE*)GlobalLock(hMem);
    memcpy(pmem, &buf[0], len);
    IStream    *stream = NULL;
    CreateStreamOnHGlobal(hMem, FALSE, &stream);
    image.Load(stream);
    stream->Release();
    GlobalUnlock(hMem);
    GlobalFree(hMem);
    return true;
}

void getCurrentTime(char *timeStr)
{
	SYSTEMTIME stLocal;
	GetLocalTime(&stLocal);

	sprintf(timeStr, "%4d-%02d-%02d %02d:%02d:%02d:%d", stLocal.wYear, stLocal.wMonth, stLocal.wDay, stLocal.wHour, stLocal.wMinute, stLocal.wSecond, stLocal.wMilliseconds);
}

void ReadIniInt(CString app, CString key, int &val, int defval)
{
	TCHAR dir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, dir);
	CString path = CString(dir) + TEXT("\\ZKBioModule.ini");

	TCHAR chr[16] = { 0 };
	CString str;

	str.Format(TEXT("%d"), defval);
	GetPrivateProfileString(app, key, str, chr, 16, path);
	val = _wtoi(chr);
}

void ReadIniFloat(CString app, CString key, float &val, float defval)
{
	TCHAR dir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, dir);
	CString path = CString(dir) + TEXT("\\ZKBioModule.ini");

	TCHAR chr[16] = { 0 };
	CString str;

	str.Format(TEXT("%f"), defval);
	GetPrivateProfileString(app, key, str, chr, 16, path);
	val = _wtof(chr);
}

void ReadIniString(CString app, CString key, CString &str, CString defstr)
{
	TCHAR dir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, dir);
	CString path = CString(dir) + TEXT("\\ZKBioModule.ini");

	GetPrivateProfileString(app, key, defstr, str.GetBufferSetLength(1024), 1024, path);
	str.ReleaseBuffer();
}

void WriteIniInt(CString app, CString key, int val)
{
	TCHAR dir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, dir);
	CString path = CString(dir) + TEXT("\\ZKBioModule.ini");

	CString str;
	str.Format(TEXT("%d"), val);
	WritePrivateProfileString(app, key, str, path);
}

void WriteIniFloat(CString app, CString key, float val)
{
	TCHAR dir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, dir);
	CString path = CString(dir) + TEXT("\\ZKBioModule.ini");

	CString str;
	str.Format(TEXT("%f"), val);
	WritePrivateProfileString(app, key, str, path);
}

void WriteIniString(CString app, CString key, CString str)
{
	TCHAR dir[MAX_PATH];
	GetCurrentDirectory(MAX_PATH, dir);
	CString path = CString(dir) + TEXT("\\ZKBioModule.ini");

	WritePrivateProfileString(app, key, str, path);
}