#!/usr/bin/env python3
#
# Copyright 2019, Sihyung Park (https://github.com/naturale0)
# 
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# A tool to convert a WOFF back to a TTF/OTF font file, in pure Python

from bs4 import BeautifulSoup
from woff2otf import convert_streams
import requests
import sys
import re
import os


def print_warning():
    print("\n============================= WARNING =============================")
    print(" Some fonts from the web might be someone's intellectual property")
    print(" and thus be protected by the corresponding laws. Please be aware")
    print(" and use this script responsibly.")
    print(" The programmer of this script and the script itself are not")
    print(" responsible in any way for problems caused by using the script.")
    print("===================================================================")
    return


def extract_webfont(URL):
    # Extract stylesheet CSS link from the web\
    global base_URL
    global font_dict
    
    if URL.find("/", 9) != -1:
        base_URL = URL[:URL.find("/", 9)]
    else:
        base_URL = URL
    
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html5lib")
    style_links = soup.find_all("link", {"rel": "stylesheet"})
    
    #href_fonts = []
    #for href in style_links:
    #    if "font" in href["href"]:
    #        href_fonts.append(href)

    
    # Get all web font(.woff) links from the CSS
    try:
        formatted_href = []
        for style_link in style_links:
            if style_link["href"].startswith("http"):
                style_URL = style_link["href"]
            elif style_link["href"].startswith("//"):
                style_URL = "https:" + style_link["href"]
            else:
                style_URL = os.path.join(base_URL.strip("/"), style_link["href"].strip("/"))
            formatted_href.append(style_URL)
            
    except (UnboundLocalError, NameError):
        raise NameError("no downloadable fonts found")

    # Remove CSS links that does not contain font-face info
    href_with_font = []
    for href in formatted_href:
        response = requests.get(href).text
        if response.find("font-face") != -1:
            href_with_font.append(href)

    # Parse font CSS into Python dictionary
    font_dict = {}
    for style_URL in href_with_font:
        response = requests.get(style_URL)
        response_txt = response.text.replace("\n", "").replace(" ", "").replace("\t", "")
        font_family_list = re.findall(r"@font-face{(.*?)}", response_txt)
        
        try:
            font_dict.update({get_font(name_link)[0]: get_font(name_link)[1] for name_link in font_family_list})
        except ValueError:
            continue

    if not font_dict:
        raise ValueError("no downloadable fonts found")

    # Prompt user input
    prompt = " Select font numbers: (e.g. 0,1)\n"
    for idx, name in enumerate(font_dict.keys()):
        prompt += f"  [{idx}] {name}\n"

    # comma-separated input. e.g. 1,2,3
    # or * (all available fonts)
    ## Download selected fonts!                             
    selected = input(prompt)
    if selected.replace(",", "").replace(" ", "").isnumeric():
        for idx in map(int, selected.replace(" ", "").split(",")):
            download_font_at(idx)
    elif selected.strip() == "*":
        for idx in range(len(font_dict)):
            download_font_at(idx)
    else:
        raise ValueError("response should be a number")


def get_font(name_link):
    links = re.findall(r'url\((.+?)\)format', name_link)

    for idx, link in enumerate(links):
        if link.endswith(".ttf"):
            is_ttf = True
            idx_ttf = idx
            break
    else:
        is_ttf = False

    for idx, link in enumerate(links):
        if link.endswith(".woff"):
            is_woff = True
            idx_woff = idx
            break
    else:
        is_woff = False

    if is_ttf:
        return os.path.basename(links[idx_ttf]), links[idx_ttf]
    elif is_woff:
        return os.path.basename(links[idx_woff]), links[idx_woff]
    else:
        raise ValueError("no downloadable fonts found")


def download_font_at(i):
    font_name = list(font_dict.keys())[i]
    if list(font_dict.values())[i].startswith("http"):
        download_URL = list(font_dict.values())[i]
    elif list(font_dict.values())[i].startswith("//"):
        download_URL = "https:" + list(font_dict.values())[i]
    else:
        download_URL = os.path.join(base_URL.strip("/"), list(font_dict.values())[i].strip("/"))
    #print(download_URL)

    # write font from the web
    if download_URL.lower().endswith(".woff"):
        response = requests.get(download_URL)
        if response.status_code == 404:
            print( "Failed to download: download page not found (404)")
            return
        woff_content = response.content
        woff_fname = font_name
        otf_fname = os.path.splitext(font_name)[0] + ".otf"
        with open(woff_fname, "wb") as wb:
            wb.write(woff_content)

        # convert woff to otf and remove woff, if needed
        woff_fhand = open(woff_fname, "rb")
        otf_fhand = open(otf_fname, "wb")
        convert_streams(woff_fhand, otf_fhand)
        woff_fhand.close()
        otf_fhand.close()

        os.remove(woff_fname)
        print(f" Font saved: ./{otf_fname}")
    elif download_URL.lower().endswith(".ttf"):
        response = requests.get(download_URL)
        if response.status_code == 404:
            print( f"Failed: {font_name} - download page not found (404)")
            return
        ttf_content = response.content
        ttf_fname = font_name
        with open(ttf_fname, "wb") as wb:
            wb.write(ttf_content)
        print(f" Font saved: ./{ttf_fname}")
    else:
        raise ValueError(f'unknown type: {download_URL.split(".")[-1]}')


def main(argv):
    if len(argv) == 2:
        print_warning()
        extract_webfont(argv[1])
    elif len(argv) > 2:
        print_warning()
        for arg in argv[1:]:
            extract_webfont(arg)
            print("\n", "="*50, "\n")
    else:
        raise ValueError("input URL does not exist")


if __name__ == "__main__":
    main(sys.argv)
