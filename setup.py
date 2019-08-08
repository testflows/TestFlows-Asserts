# Copyright 2019 Vitaliy Zakaznikov (TestFlows Test Framework http://testflows.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import datetime
from setuptools import setup

def version(major=4, minor=1):
  """Return module version.
  
  The format is: <major>.<minor>.<major revision>.<minor revision>
  
  Where major revision is based on the date YYMMDD and
  and minor revision is time HHmm.

  :param major: major version
  :param minor: minor version
  :return: version
  """
  now = datetime.utcnow()
  
  major_revision = now.strftime("%y%m%d")
  minor_revision = now.strftime("%-H%-M%-S")

  version = ".".join([str(major), str(minor), major_revision, minor_revision])

  return version

setup(
    name="testflows.asserts",
    version=version(),
    description="TestFlows - 'asserts' Assertion Library",
    long_description=open("README.rst").read(),
    author="Vitaliy Zakaznikov",
    author_email="vzakaznikov@testflows.com",
    url="http://testflows.com/asserts",
    license="Apache-2.0",
    packages=[
        "testflows.asserts",
    ],
    zip_safe=False,
    install_requires=[
      "setuptools",
    ],
    extras_require={
        "dev": [
            "sphinx",
            "testflows"
        ]
    }
)
