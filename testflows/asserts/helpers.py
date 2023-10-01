# Copyright 2019 Katteli Inc.
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
import re
import os
import inspect
import hashlib
import textwrap
import difflib

from importlib.machinery import SourceFileLoader

from testflows.asserts import error

__all__ = ["raises", "snapshot"]


def varname(s):
    """Make valid Python variable name."""
    invalid_chars = re.compile("[^0-9a-zA-Z_]")
    invalid_start_chars = re.compile("^[^a-zA-Z_]+")

    name = invalid_chars.sub("_", str(s))
    name = invalid_start_chars.sub("", name)
    if not name:
        raise ValueError(f"can't convert to valid name '{s}'")
    return name


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


# snapshot mode flags
SNAPSHOT_MODE_CHECK = 1 << 0
SNAPSHOT_MODE_UPDATE = 1 << 1
SNAPSHOT_MODE_REWRITE = 1 << 3


def write_to_snapshot(fd, name, repr_value):
    """Write entry to snapshot file object."""
    repr_value = repr_value.replace('"""', '""" + \'"""\' + r"""')
    if repr_value.endswith('"'):
        fd.write(f'''{name} = r"""{repr_value[:-1]}""" + '"'\n\n''')
    else:
        fd.write(f'''{name} = r"""{repr_value}"""\n\n''')


def rewrite_snapshot(filename):
    """Rewrite snapshot file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"does not exist: {filename}")

    module_name = f"snapshot_{hashlib.sha1(os.path.abspath(filename).encode('utf-8')).hexdigest()}"
    snapshot_module = SourceFileLoader(module_name, filename).load_module()

    with open(filename, "w") as fd:
        for name in dir(snapshot_module):
            if name.startswith("__"):
                continue
            write_to_snapshot(fd, name, getattr(snapshot_module, name))


def snapshot(
    value,
    id=None,
    output=None,
    path=None,
    name="snapshot",
    encoder=repr,
    comment=None,
    mode=SNAPSHOT_MODE_CHECK | SNAPSHOT_MODE_UPDATE,
):
    """Compare value representation to a stored snapshot.
    If snapshot does not exist, assertion passes else
    representation of the value is compared to the stored snapshot.

    Snapshot files have format:

        <test file name>[.<id>].snapshot

    :param value: value to be used for snapshot
    :param id: unique id of the snapshot file, default: `None`
    :param output: function to output the representation of the value
    :param path: custom snapshot path, default: `./snapshots`
    :param name: name of the snapshot value inside the snapshots file, default: `snapshot`
    :param encoder: custom snapshot encoder, default: `repr`
    :param comment: (deprecated)
    :param mode: mode of operation: CHECK, UPDATE, REWRITE, default: CHECK | UPDATE
    """
    name = varname(name) if name != "snapshot" else name

    class SnapshotError(object):
        def __init__(self, filename, name, snapshot_value, actual_value, diff=None):
            self.snapshot_value = snapshot_value
            self.actual_value = actual_value
            self.diff = diff
            self.filename = str(filename)
            self.name = str(name)

        def __bool__(self):
            return False

        def __repr__(self):
            r = "SnapshotError("
            r += "\nfilename=" + self.filename
            r += "\nname=" + self.name
            r += '\nsnapshot_value="""\n'
            r += textwrap.indent(self.snapshot_value, " " * 4)
            r += '""",\nactual_value="""\n'
            r += textwrap.indent(self.actual_value, " " * 4)
            r += '""",\ndiff="""\n'
            r += textwrap.indent(
                "\n".join(
                    [
                        line.strip("\n")
                        for line in difflib.unified_diff(
                            self.snapshot_value.splitlines(),
                            self.actual_value.splitlines(),
                            self.filename,
                        )
                    ]
                ),
                " " * 4,
            )
            r += '\n""")'
            return r

    try:
        repr_value = encoder(value)
    except:
        raise ValueError("failed to get representation of the snapshot value")

    if output:
        output(repr_value)

    frame = inspect.currentframe().f_back
    frame_info = inspect.getframeinfo(frame)

    id_parts = [os.path.basename(frame_info.filename)]
    if id is not None:
        id_parts.append(str(id).lower())
    id_parts.append("snapshot")

    id = ".".join(id_parts)

    if path is None:
        path = os.path.join(os.path.dirname(frame_info.filename), "snapshots")

    filename = os.path.join(path, id)

    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.exists(filename):
        module_name = f"snapshot_{hashlib.sha1(os.path.abspath(filename).encode('utf-8')).hexdigest()}"
        snapshot_module = SourceFileLoader(module_name, filename).load_module()

        if hasattr(snapshot_module, name):
            snapshot_value = getattr(snapshot_module, name)
            if not (snapshot_value == repr_value):
                if mode & SNAPSHOT_MODE_CHECK:
                    return SnapshotError(filename, name, snapshot_value, repr_value)
            else:
                return True

    if not (mode & SNAPSHOT_MODE_UPDATE):
        return SnapshotError(filename, name, "", repr_value)

    # write or update snapshot entry
    with open(filename, "a") as fd:
        write_to_snapshot(fd, name=name, repr_value=repr_value)

    if mode & SNAPSHOT_MODE_REWRITE:
        rewrite_snapshot(filename)

    return True


# define snapshot mode flags
snapshot.CHECK = SNAPSHOT_MODE_CHECK
snapshot.UPDATE = SNAPSHOT_MODE_UPDATE
snapshot.REWRITE = SNAPSHOT_MODE_REWRITE
