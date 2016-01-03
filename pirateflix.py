#!/usr/bin/env python

#python version compatibility
try:
    from urllib.request import urlopen,Request
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request
import sys
import re
try:
    from http import unescape
except ImportError:
    try:
        import html.parser
        def unescape(string):
            return html.parser.HTMLParser().unescape(string)
    except ImportError:
        import HTMLParser
        def unescape(string):
            return HTMLParser.HTMLParser().unescape(string)

url_base = "http://thepiratebay.se/search/"
if "-t" in sys.argv[1]:
    test = True
    query = sys.argv[2:]
else:
    query = sys.argv[1:]
    test = False
args = " ".join(query) # will the " " break this?
url = url_base + args
if not test:
    print("searching for torrents on piratebay using \"%s\" as search terms" % (args))
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A"}
request = Request(url,headers=headers)
page = urlopen(request).read()

result_table = re.findall("<table id=\"searchResult\">(.*)</table>",page, re.M + re.S)

if test:
    sys.exit(0 if len(result_table) > 0 else 1)

if len(result_table) < 1:
    print "No Results"
    sys.exit(1)

result_table = result_table[0]
result_list = re.findall("<tr[^>]*>(.*?)</tr>",result_table,re.M+re.S)
results = []
i = 0
for r in result_list[1:]: #first is header
    m = re.search('detName">.*?>(.*?)</a>.*?<a href="(.*?)"(.*)"detDesc">(.*?)<.*?>(.*?)<',r,re.M + re.S)
    m = m.groups()
    result = {"name": m[0], "magnet":m[1],"description":unescape(m[3]+m[4]),"VIP": True if 'alt="VIP"' in m[2] or 'alt="Trusted"' in m[2] else False}
    results.append(result)
    print "[%s]>>>" % (i), result["name"]
    print result["description"], "[VIP]" if result["VIP"] else ""
    i+=1

choice = ""
error = True
while(error):
    try:
        choice = raw_input("Which torrent to play(q to quit)?\n:")
        if not choice == "q" :
            choice = int(choice)
        error = False
    except:
        print("Invalid number. Try again")

    if "q" == choice:
        sys.exit(0)

print ("opening peerflix using %s" % (results[choice]["name"]))

import subprocess

ret = subprocess.call(["peerflix","-v", results[choice]["magnet"]],stdout=1)
