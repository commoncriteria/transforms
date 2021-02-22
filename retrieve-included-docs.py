#!/usr/bin/env python3
"""
Parses a PP retrieves the packages or PPs that are requirements.
"""

# from io import StringIO
import sys
import urllib.request
import xml.etree.ElementTree as ET
import os
import pathlib

def warn(msg):
    log(2, msg)


def err(msg):
    sys.stderr.write(msg)
    sys.exit(1)


def debug(msg):
    log(5, msg)


def log(level, msg):
    sys.stderr.write(msg)
    sys.stderr.write("\n")


def download_url(url, root, filename=None):
    """Download a file from a url and place it in root.
    Args:
        url (str): URL to download file from
        root (str): Directory to place downloaded file in
        filename (str, optional): Name to save the file under. If None, use
        the basename of the URL
    """

    root = os.path.expanduser(root)
    if not filename:
        filename = os.path.basename(url)
    fpath = os.path.join(root, filename)
    os.makedirs(root, exist_ok=True)
    try:
        print('Downloading ' + url + ' to ' + fpath)
        urllib.request.urlretrieve(url, fpath)
    except (urllib.error.URLError, IOError) as e:
        if url[:5] == 'https':
            url = url.replace('https:', 'http:')
            print('Failed download. Trying https -> http instead.'
                  ' Downloading ' + url + ' to ' + fpath)
            urllib.request.urlretrieve(url, fpath)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: <protection-profile> [directory]")
        sys.exit(0)
    # Split on equals
    if sys.argv[1] == "-":
        root = ET.fromstring(sys.stdin.read()).getroot()
    else:
        root = ET.parse(sys.argv[1]).getroot()
    dir = "."
    if len(sys.argv) == 3:
        dir = sys.argv[2]
    ns = {'cc': "https://niap-ccevs.org/cc/v1",
          'sec': "https://niap-ccevs.org/cc/v1/section",
          'htm': "http://www.w3.org/1999/xhtml"}
    ctr = 1
    for pkg in root.findall(".//cc:include-pkg", ns):
        file_name = pkg.attrib["id"] + ".xml"
        url = "".join(pkg.find("./cc:raw-url", ns).text.split())
        f_info = pathlib.Path(file_name)
        if not f_info.exists():
            download_url(url, dir, file_name)
        #
#        open( str(ctr)+".xml", 'wb').write( requests.get( url ) )


