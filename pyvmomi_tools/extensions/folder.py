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
This module implements simple extensions to the vim.Folder object in the
pyvmomi library.
"""
__author__ = "VMware, Inc."

from pyVmomi import vim


def find_by(folder, matcher_method, *args, **kwargs):
    """A generator for finding entities using a matcher_method.

    This method will search within a folder for an entity that satisfies the
    matcher_method. The matcher is called on each entity along with any
    additional arguments you pass in.

    Usage:
    ======

    code::
        for entity in folder.find_by(lambda mobj: mobj.name == 'foo'):
            print entity
            # do some work with each found entity

    code::
        def matcher(managed_object, param1, param2):
            # do stuff...

        for entity in folder.find_by(matcher, 'param1', 'param2'):
            print entity
            # do stuff...

    :type folder: vim.Folder
    :param folder: The top most folder to recursively search for the child.

    :type matcher_method: types.MethodType
    :param matcher_method: Method to call to examine the entity it must \
    return a True value on match.

    :rtype generator:
    :return: generator that produces vm.ManagedObject items.
    """
    entity_stack = folder.childEntity

    while entity_stack:
        entity = entity_stack.pop()
        if matcher_method(entity, *args, **kwargs):
            yield entity
        elif isinstance(entity, vim.Datacenter):
            # add this vim.DataCenter's folders to our search
            entity_stack.append(entity.datastoreFolder)
            entity_stack.append(entity.hostFolder)
            entity_stack.append(entity.networkFolder)
            entity_stack.append(entity.vmFolder)
        elif hasattr(entity, 'childEntity'):
            # add all child entities from this object to our search
            entity_stack.extend(entity.childEntity)


def find_by_name(folder, name):
    """Search for an entity by name.

    This method will search within the folder for an object with the name
    supplied.

    :type folder: vim.Folder
    :param folder: The top most folder to recursively search for the child.

    :type name: String
    :param name: Name of the child you are looking for, assumed to be unique.

    :rtype vim.ManagedEntity:
    :return: the one entity or None if no entity found.
    """
    # return only the first entity...
    for entity in find_by(folder, lambda e: e.name == name):
        return entity


# injection into the core vim.Folder class....
vim.Folder.find_by = find_by
vim.Folder.find_by_name = find_by_name
