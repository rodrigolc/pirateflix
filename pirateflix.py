#!/usr/bin/env python

#color class from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class colors:
    '''Colors class:
    reset all colors with colors.reset
    two subclasses fg for foreground and bg for background.
    use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green
    also, the generic bold, disable, underline, reverse, strikethrough,
    and invisible work with the main class
    i.e. colors.bold
    '''
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        lightgrey='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        lightgrey='\033[47m'

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
    print (colors.fg.green if result["VIP"] else "") + result["description"]
    print "[%s]>>>" % (i), result["name"],colors.reset

    i+=1

choice = ""
error = True
while(error):
    try:
        choice = raw_input("Which torrent to play(q to quit, m INDEX to show magnet link)?\n:")
        if re.match("^[0-9]+",choice):
            choice = int(choice)
            error = False

        elif choice == "q" :
            sys.exit(0)
        elif re.match("[m]+ [0-9]*",choice):
            g = re.findall("[m]+ [0-9]*",choice)
            choice = int(g[0].split()[1])
            print ("%s:\n%s"%(results[choice]["name"],results[choice]["magnet"]))
            sys.exit(0)
            error = False
    except Exception,e:
        print(e)
        print("Invalid number. Try again")

print ("opening peerflix using %s" % (results[int(choice)]["name"]))

import subprocess

ret = subprocess.call(["peerflix","-v", results[choice]["magnet"]],stdout=1)
