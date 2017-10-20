#!/usr/bin/python3
# -*- encoding: utf8 -*-
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2017 Marek Marczykowski-Górecki
#                               <marmarek@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import json
import subprocess
import sys

import check_git_signature

# defaults
config_defaults = {
    'sig_checker_command': './check-git-signature',
    'owner_whitelist': 'QubesOS',
    'github_api_token': '',
    'keyring': '',
    'repo_whitelist': '',
    'repo_blacklist': '',
}


def app(environ, start_response):
    config = config_defaults.copy()
    for key in config:
        env_key = 'CHECKER_CONFIG_' + key
        if env_key in os.environ:
            config[key] = os.environ[env_key]

    # input data
    untrusted_obj = json.load(environ['wsgi.input'])
    if 'pull_request' not in untrusted_obj:
        return
    if untrusted_obj['action'] not in ['opened', 'synchronize']:
        return

    untrusted_repo_full_name = untrusted_obj['pull_request']['base']['repo']['full_name']
    untrusted_pr_number = untrusted_obj['pull_request']['number']
    (untrusted_repo_owner, untrusted_repo_name) = \
        untrusted_repo_full_name.split('/', 1)
    owner_whitelist = config.get('owner_whitelist').split(' ')
    if untrusted_repo_owner not in owner_whitelist:
        raise Exception('Repository owner not whitelisted')
    repo_owner = untrusted_repo_owner
    if '/' in untrusted_repo_name:
        raise Exception('Invalid character in repository name')
    repo_whitelist = config.get('repo_whitelist')
    if repo_whitelist:
        if untrusted_repo_name not in repo_whitelist.split(' '):
            raise Exception('Repository not whitelistd')
    repo_blacklist = config.get('repo_blacklist')
    if repo_blacklist:
        if untrusted_repo_name in repo_blacklist.split(' '):
            raise Exception('Repository blacklistd')

    # input data sanitized
    repo_name = untrusted_repo_name
    pr_number = int(untrusted_pr_number)

    sig_checker_command = [
        config.get('sig_checker_command'),
        '--clone', 'https://github.com/{}/{}'.format(repo_owner, repo_name),
        '--pull-request', str(pr_number),
        '--set-commit-status',
        ]
    keyring = config.get('keyring')
    if keyring:
        sig_checker_command += ['--keyring', keyring]
    command_env = os.environ.copy()
    if config.get('github_api_token'):
        command_env['GITHUB_API_TOKEN'] = \
            config.get('github_api_token')
    try:
        check_git_signature.main(sig_checker_command[1:])
    except Exception as e:
        start_response('500 Error', [])
        import traceback
        traceback.print_exc(file=sys.stderr)
        return iter([b''])
    start_response('200 OK', [])
    return iter([b''])
