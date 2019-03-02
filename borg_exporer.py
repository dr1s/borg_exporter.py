#!/usr/bin/env python3

#   Copyright (c) 2019 Daniel Schmitz
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

import argparse
import yaml
import subprocess
import os
import json


def load_config(config_path):
    stream = open(config_path, 'r')
    config = yaml.load(stream)
    return config

def print_help(name, output_file, desc=None):
    if desc is None:
        desc = name.replace('_',' ')
    output_file.write('# HELP %s %s\n' % (name, desc))
    output_file.write('# TYPE %s gauge\n' % name )

class borg_repo():
    def __init__(self, path, password):
        self.path = path
        self.password = password

    def get_data(self, command, archive=None):
        pass_env = os.environ.copy()
        borg_command = ['borg', command, '--json', self.path]
        if not archive is None:
            borg_command[-1] = '%s::%s' % (borg_command[-1], archive)
        pass_env["BORG_PASSPHRASE"] = self.password
        proc = subprocess.run(
            borg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=pass_env)
        data = json.loads(proc.stdout.decode('utf-8'))
        return data

    def get_archives_data(self, output):
        pid = os.getpid()
        tmp_file = os.path.join(output, 'borg.prom.%i' % pid)
        output_file = open(tmp_file, 'w')
        print("Checking repo: %s" % self.path)
        info = self.get_data('info')
        archives = self.get_data('list')
        print_help('borg_repo_archives_count', output_file)
        output_file.write('borg_repo_archives_count{repo="%s"} %i\n' %
              (self.path, len(archives['archives'])))
        for s in info['cache']['stats']:
            print_help('borg_repo_%s' % s, output_file)
            output_file.write('borg_repo_%s{repo="%s"} %f\n' % (s, self.path,
                                                  info['cache']['stats'][s]))
        for archive in archives['archives']:
            info_archive = self.get_data('info', archive['archive'])
            for dump_archive in info_archive['archives']:
                name = dump_archive['name']
                duration = dump_archive['duration']
                hostname = dump_archive['hostname']
                stats = dump_archive['stats']
                print_help('borg_archive_duration', output_file)
                output_file.write(
                    'borg_archive_duration{client_hostname="%s", name="%s", repo="%s"} %f\n'
                    % (hostname, name, self.path, duration))
                for s in stats:
                    print_help('borg_archive_%s' % s, output_file)
                    output_file.write(
                        'borg_archive_%s{client_hostname="%s", name="%s", repo="%s"} %f\n'
                        % (s, hostname, name, self.path, stats[s]))
        output_file.close()

def main():
    parser = argparse.ArgumentParser(description='pihole_exporter')
    parser.add_argument('-c', '--config', help='borg_exporter config', required=True)
    parser.add_argument('-o', '--output', help='text collector dir', required=True)
    args = parser.parse_args()

    config = load_config(args.config)

    for repo in config:
        b = borg_repo(repo['repo'], repo['password'])
        b.get_archives_data(args.output)
    pid = os.getpid()
    tmp_file = os.path.join(args.output, 'borg.prom.%i' % pid)
    output_file = os.path.join(args.output, 'borg.prom')
    os.rename(tmp_file, output_file)



if __name__ == '__main__':
    main()
