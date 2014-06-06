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
This module implements simple extensions for managed objects in pyvmomi_tools.

properties
==========

Get the id for an managed object type: Folder, Datacenter, Datastore, etc.

code::
    mo = si.RetrieveContent().rootFolder
    print mo.id

"""
__author__ = "VMware, Inc."

from pyVmomi import vim

# Note (hartsock): this is naughty, break encapsulation sparingly
vim.ManagedObject.id = property(lambda self: self._moId)
