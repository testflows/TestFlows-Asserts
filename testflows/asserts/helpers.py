# Copyright 2019-2023 Katteli Inc.
# TestFlows.com Open-Source Software Testing Framework (http://testflows.com)
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
import inspect

from testflows.asserts import error
from testflows.snapshots.snapshots import *

__all__ = ["raises", "snapshot"]


class raises(object):
    """Context manager that consumes expected exceptions
    else raises an AssertionError.
    """

    def __init__(self, *excs):
        self.excs = excs
        self.exception = None
        self.frame = inspect.currentframe().f_back
        self.frame_info = inspect.getframeinfo(self.frame)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type in self.excs:
            self.exception = value
        elif type is None:
            raise AssertionError(
                error(
                    desc="exception %s was not raised" % repr(self.excs),
                    frame=self.frame,
                    frame_info=self.frame_info,
                    nodes=[],
                )
            )
        else:
            raise AssertionError(
                error(
                    desc="unexpected exception %s" % type,
                    frame=self.frame,
                    frame_info=self.frame_info,
                    nodes=[],
                )
            )
        return True
