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

"""
This module implements helper functions for vim.Task
"""
__author__ = "VMware, Inc."

import time

import pyVim.connect as connect
from pyVmomi import vim
from pyVmomi import vmodl


def build_task_filter(task):
    """A helper that builds a filter for a particular task object.

    This method builds a property filter for use with a task object and

    :rtype vim.PropertyFilter: property filter for this object
    """

    pc = connect.GetSi().content.propertyCollector

    obj_spec = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)]
    prop_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                           pathSet=[],
                                                           all=True)

    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_spec
    filter_spec.propSet = [prop_spec]
    filter = pc.CreateFilter(filter_spec, True)
    return filter


def wait_for_task(task, *args, **kwargs):
    """A helper method for blocking 'wait' based on the task class.

    This dynamic helper allows you to call .wait() on any task to keep the
    python process from advancing until the task is completed on the vCenter
    or ESX host on which the task is actually running.

    NOTE: timeout of 0 indicates 'check once, then return'

    Usage Examples
    ==============

    This method can be used in a number of ways. It is intended to be
    dynamically injected into the vim.Task object and these samples indicate
    that. The method may, however, be used free-standing if you prefer.

    Given an initial call similar to this...

    code::
        rename_task = datastore.Rename('new_name')



    simple use case
    ===============

    code::
        rename_task.wait()

    The main python process will block until the task completes on vSphere
    the datastore object will be updated automatically with the new name.

    use with callbacks
    ==================

    Simple callback use...

    code::
        def output(task, state, *args):
            print state

        rename_task.wait(queued=output,
                         running=output,
                         success=output,
                         error=output)

    Only on observed task status transition will the callback fire. That is
    if the task is observed leaving queued and entering running, then the
    callback for 'running' is fired.

    NOTE: *kwargs

    Callbacks with timeout
    ======================
    code::
        def output(task):
            print task.info.state

        rename_task.wait(timeout=3,
                         queued=output,
                         running=output,
                         success=output,
                         error=output)

    The wait method will sleep 3 seconds before re-examining the task status
    again.

    The periodic callback
    =====================
    code::
        def check_for_question(task, virtual_machine):
            if virtual_machine.runtime.question:
                handle_vm_question(virtual_machine)

        power_on_task.wait(virtual_machine, periodic=check_for_question)

    You may have a situation where you need to periodically poll the state of
    another object which might block your task's completion. An example of
    this is the PowerOn_Task operation which can be blocked by a question
    appearing on the VM's runtime. Use a periodic task to poll for such a
    change in state and handle things.

    :type task: vim.Task
    :param task: any subclass of the vim.Task object

    :rtype None: returns or raises exception

    :raises vim.RuntimeFault:
    """

    def no_op(task, *args):
        pass

    timeout = kwargs.get('timeout')

    queued_callback = kwargs.get('queued', no_op)
    running_callback = kwargs.get('running', no_op)
    success_callback = kwargs.get('success', no_op)
    error_callback = kwargs.get('error', no_op)

    periodic_callback = kwargs.get('periodic', no_op)

    last_state = None
    while True:
        periodic_callback(task, *args)

        if last_state != task.info.state:
            last_state = task.info.state

            if last_state == vim.TaskInfo.State.success:
                success_callback(task, *args)
                return

            elif last_state == vim.TaskInfo.State.queued:
                queued_callback(task, *args)

            elif last_state == vim.TaskInfo.State.running:
                running_callback(task, *args)

            elif last_state == vim.TaskInfo.State.error:
                error_callback(task, *args)
                raise task.info.error

        if timeout is not None:
            time.sleep(timeout)


# NOTE: This kind of injection usually goes at the *bottom* of a file.
vim.Task.wait = wait_for_task
vim.Task.filter = property(build_task_filter)
