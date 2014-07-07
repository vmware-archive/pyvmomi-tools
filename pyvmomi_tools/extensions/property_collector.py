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


def _build_filter_spec(managed_object):
    managed_class = managed_object.__class__
    obj_spec = [vmodl.query.PropertyCollector.ObjectSpec(obj=managed_object)]
    prop_spec = vmodl.query.PropertyCollector.PropertySpec(type=managed_class,
                                                           pathSet=[],
                                                           all=True)
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_spec
    filter_spec.propSet = [prop_spec]
    return filter_spec


def build_object_filter(property_collector, managed_object):
    """Build a Filter for collecting property changes to a managed object.

    :return: a filter you can use
    """
    filter_spec = _build_filter_spec(managed_object)
    pfilter = property_collector.CreateFilter(filter_spec, True)
    return pfilter


# inject into the PropertyCollector class
vim.PropertyCollector.build_object_filter = build_object_filter
