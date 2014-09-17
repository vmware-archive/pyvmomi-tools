#!/usr/bin/env python
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
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
from __future__ import print_function

"""
A Python script for power cycling a virtual machine. Demonstrates the use
of tasks in an asynchronous way. And how to answer virtual machine
questions in the middle of power operations.
"""

import atexit
import argparse
from six import PY2
import sys
import textwrap

from pyVim import connect
from pyVmomi import vim

from pyvmomi_tools import cli

if PY2:
    input = raw_input


def get_args():
    parser = argparse.ArgumentParser()

    cli.args.add_connection_arguments(parser)

    parser.add_argument('-n', '--name',
                        required=True,
                        action='store',
                        help='Name of the virtual_machine to look for.')

    return cli.args.prompt_for_password(parser)


args = get_args()

# form a connection...
si = connect.SmartConnect(host=args.host, user=args.user, pwd=args.password,
                          port=args.port)

# doing this means you don't need to remember to disconnect your script/objects
atexit.register(connect.Disconnect, si)

# search the whole inventory tree recursively... a brutish but effective tactic
vm = si.content.rootFolder.find_by_name(args.name)
if not isinstance(vm, vim.VirtualMachine):
    print("could not find a virtual machine with the name {0}", args.name)
    sys.exit(-1)

print("Found VirtualMachine: {0} Name: {1}", vm, vm.name)

if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
    # using a dynamic class extension for power_off
    # this is a blocking method call and the script will pause
    # while the machine powers off.
    print("powering off...")
    vm.power_off()
    print("power is off.")


def answer_question(vm):
    print("\n")
    choices = vm.runtime.question.choice.choiceInfo
    default_option = None
    if vm.runtime.question.choice.defaultIndex is not None:
        ii = vm.runtime.question.choice.defaultIndex
        default_option = choices[ii]
    choice = None
    while choice not in [o.key for o in choices]:
        print("VM power on is paused by this question:\n\n")
        print("\n".join(textwrap.wrap(vm.runtime.question.text, 60)))
        for option in choices:
            print("\t {0}: {1} ", option.key, option.label)
        if default_option is not None:
            print("default ({0}): {1}\n", default_option.label,
                  default_option.key)
        choice = input("\nchoice number: ").strip()
        print("...")
    return choice


# Sometimes we don't want a task to block execution completely
# we may want to execute or handle concurrent events. In that case we can
# poll our task repeatedly and also check for any run-time issues. This
# code deals with a common problem, what to do if a VM question pops up
# and how do you handle it in the API?
print("powering on VM {0}", vm.name)
if vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOn:

    # now we get to work... calling the vSphere API generates a task...
    task = vm.PowerOn()

    # We track the question ID & answer so we don't end up answering the same
    # questions repeatedly.
    answers = {}

    def handle_question(current_task, virtual_machine):
        # we'll check for a question, if we find one, handle it,
        # Note: question is an optional attribute and this is how pyVmomi
        # handles optional attributes. They are marked as None.
        if virtual_machine.runtime.question is not None:
            question_id = virtual_machine.runtime.question.id
            if question_id not in answers.keys():
                answer = answer_question(virtual_machine)
                answers[question_id] = answer
                virtual_machine.AnswerVM(question_id, answer)

        # create a spinning cursor so people don't kill the script...
        cli.cursor.spinner(task.info.state)

    task.poll(vm, periodic=handle_question)

    if task.info.state == vim.TaskInfo.State.error:
        # some vSphere errors only come with their class and no other message
        print("error type: {0}", task.info.error.__class__.__name__)
        print("found cause: {0}", task.info.error.faultCause)
        for fault_msg in task.info.error.faultMessage:
            print(fault_msg.key)
            print(fault_msg.message)
        sys.exit(-1)

print(".")
sys.exit(0)
