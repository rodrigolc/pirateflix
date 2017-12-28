#!/usr/bin/env python

# python version compatibility

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen
    from urllib2 import Request
import re
import subprocess

from colors import colors

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


def search(args):

    url_base = "http://thepiratebay.org/search/"

    args = " ".join(args)  # will the " " break this?
    url = url_base + args

    print("searching for torrents on piratebay using \"%s\" as search terms" %
          (args))

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) " +
        "AppleWebKit/537.75.14 (KHTML, like Gecko) " +
        "Version/7.0.3 Safari/7046A194A"
    }
    request = Request(url, headers=headers)
    page = urlopen(request).read()

    result_table = re.findall(
        "<table id=\"searchResult\">(.*)</table>", page, re.M + re.S)

    result_table = result_table[0]

    result_list = re.findall("<tr[^>]*>(.*?)</tr>", result_table, re.M + re.S)
    results = []

    for r in result_list[1:]:  # first is header
        m = re.search(
            'detName">.*?>(.*?)</a>.*?' +
            '<a href="(.*?)"(.*)"detDesc">(.*?)<.*?>(.*?)<',
            r, re.M + re.S)
        m = m.groups()
        result = {"name": m[0], "magnet": m[1], "description": unescape(
            m[3] + m[4]), "VIP": True if 'alt="VIP"' in m[2] or
            'alt="Trusted"' in m[2]
            else False}
        results.append(result)

    return results


def print_results(results):
    if len(results) <= 0:
        print ("No Results")
    i = 0
    for r in results:
        print (colors.fg.green if r["VIP"]
               else "") + "[%s]>>>" % (i), r["name"]
        print r["description"], colors.reset

        i += 1


peerflix_options = ["-d"]


def start_peerflix(magnet, index=False, vlc=True):
    global peerflix_options
    if vlc:
        peerflix_options.append("-v")
    if index:
        peerflix_options.append("-l")

    ret = subprocess.call(["peerflix"] + peerflix_options +
                          [magnet], stdout=1)

    return ret


query = raw_input("Search:")
search_results = search(query.split(' '))
print_results(search_results)

in_menu = True
while(in_menu):
    try:
        choice = raw_input(
            "Which torrent to play?\n" +
            " INDEX        - play video on vlc\n" +
            " q            - quit\n" +
            " m INDEX      - show magnet link\n" +
            " l INDEX      - list available files in torrent\n" +
            " s NEW_SEARCH - search again\n" +
            " d INDEX      - fetch file but don't play it\n" +
            " o OPTIONS    - add options to peerflix\n" +
            ":")
        if re.match("[0-9]+", choice):
            choice = int(choice)
            start_peerflix(search_results[choice]['magnet'])
        elif choice == "q":
            in_menu = False
        elif re.match("[s]+ .*", choice):
            print choice
            g = re.findall('[s]+ (.*)', choice)
            search_results = search(g[0].split())
            print_results(search_results)
        elif re.match("[o]+ .*", choice):
            print choice
            g = re.findall('[o]+ (.*)', choice)
            peerflix_options = [] # quick HACK delete options when new ones are 
                                  # introduced
            peerflix_options.extend(g[0].split())

        elif re.match("[l]+ [0-9]*", choice):
            g = re.findall("[l]+ ([0-9]*)", choice)
            choice = int(g[0])
            start_peerflix(search_results[choice]['magnet'], index=True)
        elif re.match("[m]+ [0-9]*", choice):
            g = re.findall("[m]+ ([0-9]*)", choice)
            choice = int(g[0])
            print(
                "%s:\n%s" %
                (search_results[choice]["name"],
                 search_results[choice]["magnet"])
            )
            in_menu = False
        elif re.match("[d]+ [0-9]*$", choice):
            g = re.findall('^[d]+ ([0-9]*)$', choice)
            choice = int(g[0])
            start_peerflix(search_results[choice]['magnet'], index=False,
                           vlc=False)
    except Exception, e:
        print(e)
        print("Invalid command. Try again")
