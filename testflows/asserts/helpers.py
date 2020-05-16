# Copyright 2019 Katteli Inc.
# TestFlows Test Framework (http://testflows.com)
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
import os
import inspect
import textwrap
import difflib

from testflows.asserts import error
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
            raise AssertionError(error(desc="exception %s was not raised" % repr(self.excs),
                frame=self.frame, frame_info=self.frame_info, nodes=[]))
        else:
            raise AssertionError(error(desc="unexpected exception %s" % type,
                frame=self.frame, frame_info=self.frame_info, nodes=[]))
        return True

def snapshot(value, id, output=None, path=None, encoder=repr):
    """Compare value representation to a stored snapshot.
    If snapshot does not exist, assertion passes else
    representation of the value is compared to the stored snapshot.

    Snapshot files have format:

        <test file name>.<id>.snapshot

    :param value: value
    :param output: function to output the representation of the value
    :param path: custom snapshot path, default: `./snapshots`
    :paran encoder: custom snapshot encoder, default: `repr`
    """
    class SnapshotError(object):
        def __init__(self, filename, snapshot_value, actual_value, diff=None):
            self.snapshot_value = snapshot_value
            self.actual_value = actual_value
            self.diff = diff
            self.filename = str(filename)

        def __bool__(self):
            return False

        def __repr__(self):
            r = "SnapshotError("
            r += "\nfilename=" + self.filename
            r += "\nsnapshot_value=\"\"\"\n"
            r += textwrap.indent(self.snapshot_value, " " * 4)
            r += "\"\"\",\nactual_value=\"\"\"\n"
            r += textwrap.indent(self.actual_value, " " * 4)
            r += "\"\"\",\ndiff=\"\"\"\n"
            r += textwrap.indent('\n'.join([line.strip("\n") for line in difflib.unified_diff(self.snapshot_value.splitlines(), self.actual_value.splitlines(), self.filename)]), " " * 4)
            r += "\n\"\"\")"
            return r
    try:
        repr_value = encoder(value)
    except:
        raise ValueError("failed to get representation of the snapshot value")

    if output:
        output(self.repr_value)

    frame = inspect.currentframe().f_back
    frame_info = inspect.getframeinfo(frame)

    id = '.'.join([
        os.path.basename(frame_info.filename),
        str(id).lower(),
        "snapshot"
    ])

    if path is None:
        path = os.path.join(os.path.dirname(frame_info.filename), "snapshots")

    filename = os.path.join(path, id)

    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.exists(filename):
        with open(filename, "r") as fd:
            snapshot_value = fd.read()
            if not (snapshot_value == repr_value):
                return SnapshotError(filename, snapshot_value, repr_value)
            return True
    else:
        # no snapshot, so just store the representation
        with open(filename, "w") as fd:
            fd.write(repr_value)

    return True
