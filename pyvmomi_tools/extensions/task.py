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

    The main python process will block until the task completes on vSphere.

    use with callbacks
    ==================

    Simple callback use...

    code::
        def output(task, *args):
            print task.info.state

        rename_task.wait(queued=output,
                         running=output,
                         success=output,
                         error=output)

    Only on observed task status transition will the callback fire. That is
    if the task is observed leaving queued and entering running, then the
    callback for 'running' is fired.

    :type task: vim.Task
    :param task: any subclass of the vim.Task object

    :rtype None: returns or raises exception

    :raises vim.RuntimeFault:
    """

    def no_op(task, *args):
        pass

    queued_callback = kwargs.get('queued', no_op)
    running_callback = kwargs.get('running', no_op)
    success_callback = kwargs.get('success', no_op)
    error_callback = kwargs.get('error', no_op)

    si = connect.GetSi()
    pc = si.content.propertyCollector
    filter = build_task_filter(task)

    try:
        version, state = None, None

        # Loop looking for updates till the state moves to a completed state.
        waiting = True
        while waiting:
            update = pc.WaitForUpdates(version)
            version = update.version
            for filterSet in update.filterSet:
                for objSet in filterSet.objectSet:
                    task = objSet.obj
                    for change in objSet.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if state == vim.TaskInfo.State.success:
                            success_callback(task, *args)
                            waiting = False

                        elif state == vim.TaskInfo.State.queued:
                            queued_callback(task, *args)

                        elif state == vim.TaskInfo.State.running:
                            running_callback(task, *args)

                        elif state == vim.TaskInfo.State.error:
                            error_callback(task, *args)
                            raise task.info.error

    finally:
        if filter:
            filter.Destroy()


def poll_task(task, *args, **kwargs):
    """A helper method for polling state changes on the task class.

    Similar to wait_for_task this helper introduces a sleep_seconds optional
    kwarg and a 'periodic' call back that can be used to check vCenter status
    or interact with vCenter periodically while we wait for a task to complete.
    The prime use-case for this utility is the power_on case described below.

    This dynamic helper allows you to call .wait() on any task to keep the
    python process from advancing until the task is completed on the vCenter
    or ESX host on which the task is actually running.

    NOTE: sleep_seconds of 0 indicates check as fast as possible. This
    mode will generate a great deal of network traffic.

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

    use with sleep_seconds
    ======================
    code::
        rename_task.wait(sleep_seconds=0)

    The default sleep_seconds is 1, meaning the vCenter server is polled at
    most 1 time every 1 second. If you set sleep_seconds to 0, the vCenter
    server will be polled as fast as possible. This has the tendency to create
    a great deal of network traffic.

    code::
        rename_task.wait(sleep_seconds=3)

    The process will wait 3 seconds between polling vCenter for task status.
    The default is to wait 1 second between polling vCenter for task updates.

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

    Callbacks with sleep_seconds
    ============================
    code::
        def output(task):
            print task.info.state

        rename_task.wait(sleep_seconds=3,
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

    sleep_seconds = kwargs.get('sleep_seconds', 1)

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

        if sleep_seconds is not None:
            time.sleep(sleep_seconds)


# NOTE: This kind of injection usually goes at the *bottom* of a file.
vim.Task.poll = poll_task
vim.Task.wait = wait_for_task
vim.Task.is_alive = property(lambda t: t.info.state not in [
    vim.TaskInfo.State.success, vim.TaskInfo.State.error])
vim.Task.filter = property(build_task_filter)
