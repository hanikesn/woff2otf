#!/usr/bin/env python3
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
    base_URL = URL[:URL.find("/", 9)]

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html5lib")
    style_links = soup.find_all("link", {"rel": "stylesheet"})

    for href in style_links:
        if "font" in href["href"]:
            style_link = href

    
    # Get all web font(.woff) links from the CSS
    try:
        if style_link["href"].startswith("http"):
            style_URL = style_link["href"]
        elif style_link["href"].startswith("//"):
            style_URL = "https:" + style_link["href"]
        else:
            style_URL = os.path.join(base_URL.strip("/"), style_link["href"].strip("/"))
        response = requests.get(style_URL)
    except (UnboundLocalError, NameError):
        raise NameError("no downloadable fonts found")
    style_URL


    # Parse font CSS into Python dictionary
    def get_font(name_link):
        links = re.findall(r'url\((.+?)\)format', name_link)
        #print(links)

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

    response_txt = response.text.replace("\n", "").replace(" ", "").replace("\t", "")
    font_family_list = re.findall(r"@font-face{(.*?)}", response_txt)
    font_family_list

    font_dict = {get_font(name_link)[0]: get_font(name_link)[1] for name_link in font_family_list}

    font_dict
    if not font_dict:
        raise ValueError("no downloadable fonts found")

    # Prompt user input
    prompt = " Select font numbers: (e.g. 0,1)\n"
    for idx, name in enumerate(font_dict.keys()):
        prompt += f"  [{idx}] {name}\n"

    # comma-separated input. e.g. 1,2,3
    selected = input(prompt)
    if selected.replace(",", "").replace(" ", "").isnumeric():
        for i in map(int, selected.replace(" ", "").split(",")):
            font_name = list(font_dict.keys())[i]
            if list(font_dict.values())[i].startswith("http"):
                download_URL = list(font_dict.values())[i]
            elif list(font_dict.values())[i].startswith("//"):
                download_URL = "https:" + list(font_dict.values())[i]
            else:
                download_URL = os.path.join(base_URL.strip("/"), list(font_dict.values())[i].strip("/"))

            # write font from the web
            if download_URL.lower().endswith(".woff"):
                woff_content = requests.get(download_URL).content
                woff_fname = font_name
                otf_fname = font_name.split(".")[-2] + ".otf"
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
                ttf_content = requests.get(download_URL).content
                ttf_fname = font_name
                with open(ttf_fname, "wb") as wb:
                    wb.write(ttf_content)
                print(f" Font saved: ./{ttf_fname}")
            else:
                raise ValueError(f'unknown type: {download_URL.split(".")[-1]}')

    else:
        raise ValueError("response should be a number")


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