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


class borg_repo():
    def __init__(self, path, password):
        self.path = path
        self.password = password
        self.data = dict()
        self.data['path'] = path

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

    def get_archives_data(self):
        print("Checking repo: %s" % self.path)
        info = self.get_data('info')
        archives = self.get_data('list')
        self.data['archive_count'] = len(archives['archives'])
        self.data['stats'] = info['cache']['stats']
        self.data['archives'] = list()
        for archive in archives['archives']:
            info_archive = self.get_data('info', archive['archive'])
            for dump_archive in info_archive['archives']:
                archive_dict = dict()
                archive_dict['name'] = dump_archive['name']
                archive_dict['duration'] = dump_archive['duration']
                archive_dict['stats'] = dump_archive['stats']
                archive_dict['hostname'] = dump_archive['hostname']
                self.data['archives'].append(archive_dict)


class borg_exporter():
    def __init__(self, config):
        self.config = config
        self.data = list()
        self.process_repos()

    def print_help(self, metric_name, desc=None):
        if desc is None:
            desc = metric_name.replace('_', ' ')
        output = '# HELP %s %s\n' % (metric_name, desc)
        output += '# TYPE %s gauge\n' % metric_name
        return output

    def process_repos(self):
        for repo in self.config:
            if os.path.exists(repo['repo']) and os.path.isdir(repo['repo']):
                b = borg_repo(repo['repo'], repo['password'])
                b.get_archives_data()
                self.data.append(b.data)
            else:
                print('repo not found, skipping: %s' % repo['repo'])

    def generate_prometheus_metrics(self):
        output = self.print_help('borg_repo_archives_count')
        for r in self.data:
            output += 'borg_repo_archives_count{repo="%s"} %i\n' % (
                r['path'], r['archive_count'])

        stats_keys = [*self.data[0]['stats']]
        for s in stats_keys:
            output += self.print_help('borg_repo_%s' % s)
            for r in self.data:
                output += 'borg_repo_%s{repo="%s"} %f\n' % (s, r['path'],
                                                            r['stats'][s])

        output += self.print_help('borg_archive_duration')
        for r in self.data:
            if len(r['archives']) > 0:
                for a in r['archives']:
                    archive_stats_keys = [*a['stats']]
                    output += 'borg_archive_duration{client_hostname='
                    output += '"%s", name="%s", repo="%s"} %f\n' % (
                        a['hostname'], a['name'], r['path'], a['duration'])

        for s in archive_stats_keys:
            output += self.print_help('borg_archive_%s' % s)
            for r in self.data:
                for a in r['archives']:
                    output += 'borg_archive_'
                    output += '%s{client_hostname="%s", name="%s", repo="%s"} %f\n' % (
                        s, a['hostname'], a['name'], r['path'],
                        a['stats'][s])
        return output

    def write_to_file(self, filename):
        metrics_string = self.generate_prometheus_metrics()
        tmp_file = os.path.join('%s.%i' % (filename, os.getpid()))
        output_file = open(tmp_file, 'w')
        output_file.write(metrics_string)
        output_file.close()
        os.rename(tmp_file, filename)


def main():
    parser = argparse.ArgumentParser(description='pihole_exporter')
    parser.add_argument(
        '-c', '--config', help='borg_exporter config', required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    be = borg_exporter(config['repos'])
    be.write_to_file(config['output_file'])


if __name__ == '__main__':
    main()
