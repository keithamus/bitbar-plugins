#!/usr/bin/env python
import re
import os
import subprocess
import urllib2

allowed_image_content_types = [ 'image/png', 'image/jpeg' ]
required_metadata = [ 'author', 'author.github', 'title', 'image' ]
required_shebangs = {
    '.sh': '#!/usr/bin/env bash',
    '.py': '#!/usr/bin/env python',
    '.rb': '#!/usr/bin/env ruby',
    '.js': '#!/usr/bin/env node',
    '.php': '#!/usr/bin/env php',
    '.pl': '#!/usr/bin/env perl',
    '.swift': '#!/usr/bin/env xcrun swift',
}
linter_command = {
    '.sh': [ 'shellcheck' ],
    '.py': [ 'pyflakes' ],
    '.rb': [ 'rubocop' ],
    '.js': [ 'standard' ],
    '.php': [ 'php', '-l' ],
    '.pl': [ 'perl', '-MO=Lint'],
    '.swift': [ 'xcrun', '-sdk', 'macosx', 'swiftc' ],
}
error_count = 0
DEBUG = True
def debug(s):
    if DEBUG:
        print "\033[1;44mDBG!\033[0;0m %s\n" % s

def error(s):
    global error_count
    error_count += 1
    print "\033[1;41mERR!\033[0;0m %s\n" % s

for root, dirs, files in os.walk("."):
    for f in files:
        file_full_path = os.path.join(root, f).strip()
        file_short_name, file_extension = os.path.splitext(file_full_path)
        debug("Found file %s" % file_full_path)

        print

        if f == "README.md" or f.startswith("."):
            debug("skipping file checks for %s" % file_full_path)
            continue

        if not required_shebangs.get(file_extension, False):
            error("%s unrecognized file extension" % file_full_path)
            continue

        if not os.access(file_full_path, os.R_OK):
            error("%s not readable" % file_full_path)
            pass

        if not os.access(file_full_path, os.X_OK):
            error("%s not executable" % file_full_path)

        metadata = {}
        with open(os.path.join(root, f), "r") as fp:
            first_line = fp.readline().strip()
            expected_shebang = required_shebangs.get(file_extension, first_line).strip()
            if first_line != expected_shebang:
                error("%s has incorrect shebang.\n  Got %s\n  Wanted %s" % (file_full_path, first_line, expected_shebang))

            for line in fp:
                match = re.search("<bitbar.(?P<lho_tag>[^>]+)>(?P<value>[^<]+)</bitbar.(?P<rho_tag>[^>]+)>", line)
                if match is not None:
                    if match.group('lho_tag') != match.group('rho_tag'):
                        error('%s includes mismatched metatags: %s', (file_full_path, line))
                    else:
                        metadata[match.group('lho_tag')] = match.group('value')

        for key in required_metadata:
            if key not in metadata:
                error('%s missing metadata for %s' % (file_full_path, key))

        if metadata.get('image', False):
            response = urllib2.urlopen(metadata['image'])
            response_content_type = response.info().getheader('Content-Type')
            if response_content_type in allowed_image_content_types:
                error('%s has bad content type: %s' % (file_full_path, response_content_type))

        if linter_command.get(file_extension, False):
            command = list(linter_command[file_extension])
            command.append(file_full_path)
            debug('running %s' % command)
            lint_exit_code = subprocess.call(command)
            if lint_exit_code > 0:
                error('%s failed linting, see above errors' % file_full_path)

    skip = [d for d in dirs if d.startswith(".")]
    for d in skip:
        debug('skipping directory %s' % d)
        dirs.remove(d)


if error_count > 0:
    error('failed with %i errors' % error_count)
    exit(1)
