pyvmomi-tools
=============

> Additional community developed python packages to help you work with pyvmomi

This project is an incubator project for additional pyVmomi based tools and
libraries as needed by the development community.

Warning
=======

pyVmomi tools is currently in Alpha and is experimental, use at your own risk.

Why
===

Developers working with pyVmomi often end up creating the same helpers and
utilities for themselves. This project represents a place for everyone to
share those tools with each other.

Tool Incubator
===============

Utilities started here may be graduated to free-standing libraries distributed
independently of this library. A graduated library would be expressed as a
dependency for this library. For example if pyvmomi_tools.foo were distributed
first as part of this library but graduated to pyvmomi-foo (a stand-alone
library) then this project would express in its requirements an explicit
dependency on pyvmomi-foo.

Module, driver, and service developers will benefit from the ability to only
import the library elements they need while scripting developers benefit from
having a single top-level meta package to import for all the latest and best
tools.

Contributing
============

Follow the github contribution process. Please be sure that any pull request
makes reference to an approved issue. Smaller commits are better, but cohesive
requests are best. That is, one pull request should equal one feature. One
commit should equal one issue/concern/bug-fix.

* All contributed code becomes property of the project.
* All Copyrights revert to VMware, Inc.
* All code remains licensed under the LICENSE distributed with this project

Coding Standards
================

* follow [pep8](http://legacy.python.org/dev/peps/pep-0008/)
* [document](https://docs.python.org/devguide/documenting.html)
** types, exceptions, return types should all be documented
* [unit test](https://docs.python.org/2/library/unittest.html)
