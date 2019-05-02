# WebFontUtil

This is a small utility specialized in extracting and converting web fonts.  
It uses Python 3, so you need to have it installed in order to run it.

## Usage
### 1. woff2otf
To run the script, simply invoke it from the command line:
```
./woff2otf.py font.woff font.otf
```

The first parameter is the source file (the WOFF) font, and the second parameter is the output file (in OTF format).

### 2. web font extractor
To run the script. type in the following command in terminal.
```
./extract_webfont.py 'https://sample1.com'
```

make sure the URLs have 'http' or 'https' header in front of it, and are wrapped with quotation marks(`'`).

Then, the script will extract all the fonts it can extract from the URL and prompt them as follows.

```
============================= WARNING =============================
 Some fonts from the web might be someone's intellectual property
 and thus be protected by the corresponding laws. Please be aware
 and use this script responsibly.
 The programmer of this script and the script itself are not
 responsible in any way for problems caused by using the script.
===================================================================
 Select font numbers: (e.g. 0,1)
  [0] Together-KwonJungae.woff
  [1] KakaoLight.woff
  [2] KakaoRegular.woff
  [3] KakaoBold.woff
  [4] NotoSans-Light.woff
  [5] NotoSans-Medium.woff
  [6] NotoSans-Regular.woff
```


Just select corresponding numbers of fonts you want to download. In this example, 4, 5, 6.

```
 Font saved: ./NotoSans-Light.otf
 Font saved: ./NotoSans-Medium.otf
 Font saved: ./NotoSans-Regular.otf
```
