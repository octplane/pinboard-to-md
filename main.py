#!/usr/bin/env python

import pinboard
import frontmatter
import ConfigParser, os
import unicodedata
import re
from datetime import date


def seo(string):
    r = unicodedata.normalize('NFKD', string).encode('cp1256','ignore')
    r = unicode(re.sub('[^\w\s-]','',r).strip().lower())
    r = re.sub('[-\s]+','-',r)
    return r


def post_filename(title):
    now = date.today()
    prefix = date.strftime(now, "%Y-%m-%d-")
    return prefix + seo(title)


class Blogpost(object):
    def __init__(self, bookmark):
        self.bookmark = bookmark
        self.frontmatter = frontmatter.loads(bookmark.extended)

    def slug(self):
        t = self.frontmatter.get("title", self.bookmark.description)
        self.frontmatter["title"] = t
        self.frontmatter["date"] = date.strftime(self.bookmark.time, "%Y-%m-%d %H:%m:%S")
        self.frontmatter["layout"] = "pinboard"
        self.frontmatter["reference"] = self.bookmark.url
        tags = self.bookmark.tags
        if "us" in tags:
            tags.remove("us")
            self.frontmatter["lang"] = "us"
        elif "fr" in tags:
            tags.remove("fr")
            self.frontmatter["lang"] = "fr"


        self.frontmatter["tags"] = tags
        self.frontmatter["tags"].remove("blog")
        self.frontmatter["generator"] = "pinboard-to-md"

        fname = date.strftime(self.bookmark.time, "%Y-%m-%d-%H-%m")
        if len(fname) > 25:
            return fname[:25]
        else:
            return fname

    def fname(self):
        return self.slug() + ".md"

    def fcontent(self):
        return frontmatter.dumps(self.frontmatter)

    def export(self, export_folder):
        fname = os.path.join(export_folder, self.fname())
        f = open(fname, 'w')
        f.write(self.fcontent().encode('utf-8'))
        f.close()

config = ConfigParser.ConfigParser()
config.read(os.path.expanduser('~/.pinboardrc'))

TOKEN = config.get("pinboard", "token")
LOCATION  = config.get("export", "location")

pb = pinboard.Pinboard(TOKEN)

# print pb.posts.recent(tag=["blog"], parse_response=False).read()

for post in pb.posts.recent(tag=["blog"])['posts']:
    b = Blogpost(post)
    b.export(LOCATION)
