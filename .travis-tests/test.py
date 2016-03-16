import re
import os
import sys

for root, dirs, files in os.walk("."):
    for f in files:
        if f == "README.md" or f == "test.py":
            continue
        if f.startswith("."):
            continue
        if not os.access(os.path.join(root, f), os.X_OK):
            print "%s not executable" % os.path.join(root, f)
            pass

        author = github = title = version = image = False
        with open(os.path.join(root, f), "r") as fp:
            for line in fp:
                if line[0] != "#":
                    continue
                if re.search("<bitbar.author>[^<]+</bitbar.author>", line, re.I):
                    author = True
                if re.search("<bitbar.author.github>[^<]+</bitbar.author.github>", line, re.I):
                    github = True
                if re.search("<bitbar.title>[^<]+</bitbar.title>", line, re.I):
                    title = True
                if re.search("<bitbar.version>[^<]+</bitbar.version>", line, re.I):
                    version = True
                if re.search("<bitbar.image>[^<]+</bitbar.image>", line, re.I):
                    image = True
        if not author:
            print "Missing bitbar.author in %s" % os.path.join(root, f)
        if not github:
            print "Missing bitbar.author.github in %s" % os.path.join(root, f)
        if not title:
            print "Missing bitbar.title in %s" % os.path.join(root, f)
        if not version:
            print "Missing bitbar.version in %s" % os.path.join(root, f)
        if not image:
            print "Missing bitbar.image in %s" % os.path.join(root, f)
    skip = [d for d in dirs if d.startswith(".")]
    for d in skip:
        dirs.remove(d)
