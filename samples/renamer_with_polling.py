#!/usr/bin/env python
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A Python script for changing the name of an object. Demonstrates the use
of tasks in an asynchronous way.
"""

import atexit
import argparse
import getpass

from pyVim import connect
from pyvmomi_tools.cli import cursor


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-o', '--port',
                        required=False,
                        action='store',
                        help="port to use, default 443", default=443)

    parser.add_argument('-n', '--name',
                        required=True,
                        action='store',
                        help='Name of the entity to look for.')

    parser.add_argument('-r', '--new_name',
                        required=False,
                        action='store',
                        help='New name of the entity.')

    _args = parser.parse_args()
    if _args.password is None:
        _args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (_args.host, _args.user))

    return _args


args = get_args()

# form a connection...
si = connect.SmartConnect(host=args.host, user=args.user, pwd=args.password,
                          port=args.port)

# doing this means you don't need to remember to disconnect your script/objects
atexit.register(connect.Disconnect, si)

# search the whole inventory tree recursively... a brutish but effective tactic
entity = si.content.rootFolder.find_by_name(args.name)

if entity is None:
    print "A object named %s could not be found" % args.name
    exit()

if args.new_name:
    new_name = args.new_name
else:
    # just because we want the script to do *something*
    new_name = args.name + "0"

print
print "name        : %s" % entity.name
print
print "    renaming from %s to %s" % (args.name, new_name)
print

# rename creates a task...
task = entity.Rename(new_name)

print "task status: "

# demonstrate task state polling
while task.is_alive:
    cursor.spinner('renaming')
print

print
print "rename finished"
print
