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


with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('test-requirements.txt') as f:
    required_for_tests = f.read().splitlines()

setup(name='pyvmomi-tools',
      # NOTE: Versions will be 0.1.0, 1.0.0, 1.1.0 and so on
      version='DEVELOPMENT',
      description='VMware vSphere Python SDK Community Tools',
      author='VMware, Inc.',
      author_email='hartsocks@vmware.com',
      url='https://github.com/vmware/pyvmomi-tools',
      packages=['pyvmomi_tools'],
      install_requires=required,
      dependency_links=['https://github.com/vmware/pyvmomi',
                        'https://github.com/kevin1024/vcrpy'],
      license='Apache',
      long_description=read('README.rst'),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Developers',
          'Environment :: No Input/Output (Daemon)',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Distributed Computing',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: Unix',
          'Operating System :: MacOS',
      ],
      test_suite='tests',
      tests_require=required_for_tests,
      zip_safe=True)
