# VMware vSphere Python SDK Community Tools Incubator
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

import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pyvmomi-tools',
      version='5.5.0-2014.dev',
      description='VMware vSphere Python SDK Community Tools',
      author='VMware, Inc.',
      author_email='hartsocks@vmware.com',
      url='https://github.com/vmware/pyvmomi-tools',
      packages=['pyvmomi_tools'],
      install_requires=['pyvmomi'],
      dependency_links=['https://github.com/vmware/pyvmomi'],
      license='Apache',
      long_description=read('README.md'),
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Development Status :: 4 - Beta",
          "Environment :: No Input/Output (Daemon)",
          "Intended Audience :: Information Technology",
          "Intended Audience :: System Administrators",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: System :: Distributed Computing"
      ],
      zip_safe=True)
