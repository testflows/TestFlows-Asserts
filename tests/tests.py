# Copyright 2019 Vitaliy Zakaznikov, TestFlows Test Framework (http://testflows.com)
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
import sys
import re
import tempfile

from testflows.core import main
from testflows.core import Test as TestBase
from testflows.asserts import error, errors, this, raises, snapshot

def snap(value):
    """Take a snapshot of the value. If the value is an
    AssertionError with an error object then do not
    include the "where section".
    """
    if isinstance(value, AssertionError) and value.args:
        if isinstance(value.args[0], error):
            err = value.args[0]
            err.where_section = False
            return err.generate_message()
        if isinstance(value.args[0], errors):
            err = value.args[0]
            err.where_section = False
            return str(err)
    return repr(value)

class Test(TestBase):
    def run(self):
        with self.test("errors") as suite:
            with suite.test("errors no fails") as test:
                with errors():
                    assert True
                    assert 1 == 1

            with suite.test("errors") as test:
                with raises(AssertionError) as e:
                    with errors():
                        assert True
                        assert False, "boo" 
                test.note(e.exception)
                with this() as that:
                    assert that(snapshot(e.exception, "errors-errors", encoder=snap)), error()

            with suite.test("soft error no fails") as test:
                with errors() as soft:
                    with soft.error():
                        assert True
                    with soft.error():
                        assert 1 == 1

            with suite.test("soft errors") as test:
                with raises(AssertionError) as e:
                    with errors() as soft:
                        with soft.error():
                            assert False, "boo"
                        with soft.error():
                            assert False, "boo2"
                        assert True
                test.note(e.exception)
                with this() as that:
                    assert that(snapshot(e.exception, "errors-soft-errors", encoder=snap)), error()

            with suite.test("mixed errors no fails") as test:
                with errors() as soft:
                    assert True
                    with soft.error():
                        assert True
                    assert "a" == "a"
                    with soft.error():
                        assert True

            with suite.test("mixed errors") as test:
                with raises(AssertionError) as e:
                    with errors() as soft:
                        with soft.error():
                            assert False, "boo"
                        assert True
                        assert False, "boo2"
                        # should not get here as the assertion above
                        # should cause an exception
                        assert 1/0
                test.note(e.exception)
                with this() as that:
                    assert that(snapshot(e.exception, "errors-mixed-errors", encoder=snap)), error()

        with self.test("helpers") as suite:
            with suite.test("raises") as subsuite:
                with subsuite.test("not raised") as test:
                    with raises(AssertionError) as e:
                        with raises(AssertionError):
                            pass
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "raises-not-raised", encoder=snap)), error()

                with subsuite.test("unexpected exception") as test:
                    with raises(AssertionError) as e:
                        with raises(AssertionError):
                            raise ValueError("error")
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "raises-unexpected-exception", encoder=snap)), error()

                with subsuite.test("ok") as test:
                    with raises(ValueError) as e:
                        raise ValueError("error")
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "raised-ok", encoder=snap)), error()

        with self.test("assertions") as suite:
            with suite.test("multiline") as subsuite:
                with subsuite.test("implicit") as test:
                    with raises(AssertionError) as e:
                        assert (1,
                                2) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "multiline-implicit", encoder=snap)), error()

                with suite.test("explicit") as test:
                    with raises(AssertionError) as e:
                        assert "hello" == "foo bar"\
                            and 3 == 3\
                            and 1 > 1 or 1>1 or 3>3 or 4>+4, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "multiline-explicit", encoder=snap)), error()

            with suite.test("this") as subsuite:
                with subsuite.test("assert with file read") as test:
                    with tempfile.TemporaryFile("w+") as fp:
                        fp.write("hello")
                        fp.seek(0)
                        with raises(AssertionError) as e, this() as that:
                            assert not that(fp.read()), error()
                        test.note(e.exception)
                        with this() as that:
                            assert that(snapshot(e.exception, "this-assert_with_file_read", encoder=snap)), error()

                with subsuite.test("assert with list append") as test:
                    some_list = []
                    with raises(AssertionError) as e, this() as that:
                        assert that(some_list.append(2)) == [1], error()
                    test.note(e.exception)
                    with test.test("assert that list did not change"):
                        assert some_list == [2], error()
                    with this() as that:
                        assert that(snapshot(e.exception, "this-assert_with_list_append", encoder=snap)), error()

            with suite.test("func") as subsuite:
                with subsuite.test("args") as test:
                    vs = []
                    def foo(x,y,z):
                        vs.append((x,y,z))
                        return x,y,z
                    with raises(AssertionError) as e:
                        assert foo(1,2,3) is False, error()
                    test.note(e.exception)
                    with test.test("assert that args are the same"):
                        assert vs[0] == vs[1], error()
                    with test.test("assert exception snapshot value"):
                        with this() as that:
                            assert that(snapshot(e.exception, "func-args", encoder=snap)), error()

                with subsuite.test("*vargs") as test:
                    vs = []
                    def foo(*x):
                        test.note(x)
                        vs.append(x)
                        return x
                    with raises(AssertionError) as e:
                        assert foo(*[1,2]) is False, error()
                    test.note(e.exception)
                    with test.test("assert *vargs are the same"):
                        assert vs[0] == vs[1]
                    with this() as that:
                        assert that(snapshot(e.exception, "func-vargs", encoder=snap)), error()

                with subsuite.test("**kwargs") as test:
                    vs = []
                    def foo(**x):
                        test.note(x)
                        vs.append(x)
                        return x
                    with raises(AssertionError) as e:
                        assert foo(x=1,y=2) is False, error()
                    test.note(e.exception)
                    with test.test("assert **kwargs are the same"):
                        assert vs[0] == vs[1]
                    with this() as that:
                        assert that(snapshot(e.exception, "func-kwargs", encoder=snap)), error()

                with subsuite.test("args *vargs **kwargs") as test:
                    vs = []
                    def foo(x,*y,**z):
                        test.note((x, y, z))
                        vs.append((x, y, z))
                        return x, y, z
                    with raises(AssertionError) as e:
                        assert foo(1,*[2],z=3) is False, error()
                    test.note(e.exception)
                    with test.test("assert args, *vargs, **kwargs are the same"):
                        assert vs[0] == vs[1]
                    with this() as that:
                        assert that(snapshot(e.exception, "func-args_vargs_kwargs", encoder=snap)), error()

            with suite.test("boolean ops") as subsuite:
                with subsuite.test("and") as test:
                    with raises(AssertionError) as e:
                        assert 1 and 0, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-and", encoder=snap)), error()

                with subsuite.test("multiple and") as test:
                    with raises(AssertionError) as e:
                        assert 1 and 2 and 3 and 0, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-multiple-and", encoder=snap)), error()

                with subsuite.test("or") as test:
                    with raises(AssertionError) as e:
                        assert 0 or '', error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-or", encoder=snap)), error()

                with subsuite.test("multiple or") as test:
                    with raises(AssertionError) as e:
                        assert 0 or '' or False or None, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-multiple-or", encoder=snap)), error()

            with suite.test("binary ops") as subsuite:
                with subsuite.test("add") as test:
                    with raises(AssertionError) as e:
                        assert 1 + 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-add", encoder=snap)), error()

                with subsuite.test("sub") as test:
                    with raises(AssertionError) as e:
                        assert 1 - 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-sub", encoder=snap)), error()

                with subsuite.test("mul") as test:
                    with raises(AssertionError) as e:
                        assert 1 * 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-mul", encoder=snap)), error()

                with subsuite.test("div") as test:
                    with raises(AssertionError) as e:
                        assert 1 / 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-div", encoder=snap)), error()

                with subsuite.test("mod") as test:
                    with raises(AssertionError) as e:
                        assert 1 % 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-mod", encoder=snap)), error()

                with subsuite.test("pow") as test:
                    with raises(AssertionError) as e:
                        assert 1 ** 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-pow", encoder=snap)), error()

                with subsuite.test("lshift") as test:
                    with raises(AssertionError) as e:
                        assert 1 << 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-lshift", encoder=snap)), error()

                with subsuite.test("rshift") as test:
                    with raises(AssertionError) as e:
                        assert 1 >> 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-rshift", encoder=snap)), error()

                with subsuite.test("bitOr") as test:
                    with raises(AssertionError) as e:
                        assert 1 | 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-bitOr", encoder=snap)), error()

                with subsuite.test("bitXor") as test:
                    with raises(AssertionError) as e:
                        assert 1 ^ 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-bitXor", encoder=snap)), error()

                with subsuite.test("bitAnd") as test:
                    with raises(AssertionError) as e:
                        assert 1 & 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-bitAnd", encoder=snap)), error()

                with subsuite.test("floor div") as test:
                    with raises(AssertionError) as e:
                        assert 1 // 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-floor-div", encoder=snap)), error()

                with subsuite.test("mixed ops") as test:
                    with raises(AssertionError) as e:
                        assert 1 + 3 - 4 * 5 ** 1 >> 1 << 3 % 5 | 2 ^ 5 & 6 // 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-mixed-ops", encoder=snap)), error()

            with suite.test("unary ops") as subsuite:
                with subsuite.test("invert") as test:
                    with raises(AssertionError) as e:
                        assert ~4 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-invert", encoder=snap)), error()

                with subsuite.test("not") as test:
                    with raises(AssertionError) as e:
                        assert not 4 is 4, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-not", encoder=snap)), error()

                with subsuite.test("uadd") as test:
                    with raises(AssertionError) as e:
                        assert +4 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-uadd", encoder=snap)), error()

                with subsuite.test("usub") as test:
                    with raises(AssertionError) as e:
                        assert -4 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-usub", encoder=snap)), error()

            with suite.test("compare ops") as subsuite:
                with subsuite.test("eq") as test:
                    with raises(AssertionError) as e:
                        assert 1 == 2, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq", encoder=snap)), error()

                with subsuite.test("eq str") as test:
                    with raises(AssertionError) as e:
                        assert "1:a\n2:a\n3:c" == "1:a\n2:b\n3:c", error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq-str", encoder=snap)), error()

                with subsuite.test("eq tuple") as test:
                    with raises(AssertionError) as e:
                        assert (1,2,3) == (1,1,3), error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq-tuple", encoder=snap)), error()

                with subsuite.test("eq list") as test:
                    with raises(AssertionError) as e:
                        assert [1,2,3] == [1,1,3], error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq-list", encoder=snap)), error()

                with subsuite.test("eq set") as test:
                    with raises(AssertionError) as e:
                        assert {1,2,3} == {1,2,3,4}, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq-set", encoder=snap)), error()

                with subsuite.test("eq dict") as test:
                    with raises(AssertionError) as e:
                        assert {1:"a", 2:"a", 3:"c"} == {1:"a", 2:"b", 3:"c"}, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq-dict", encoder=snap)), error()

                with subsuite.test("ne") as test:
                    with raises(AssertionError) as e:
                        assert 1 != 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-ne", encoder=snap)), error()

                with subsuite.test("lt") as test:
                    with raises(AssertionError) as e:
                        assert 1 < 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-lt", encoder=snap)), error()

                with subsuite.test("le") as test:
                    with raises(AssertionError) as e:
                        assert 1 <= 0, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-le", encoder=snap)), error()

                with subsuite.test("gt") as test:
                    with raises(AssertionError) as e:
                        assert 1 > 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-gt", encoder=snap)), error()

                with subsuite.test("ge") as test:
                    with raises(AssertionError) as e:
                        assert 1 >= 2, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-ge", encoder=snap)), error()

                with subsuite.test("is") as test:
                    with raises(AssertionError) as e:
                        assert 1 is 2, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-is", encoder=snap)), error()

                with subsuite.test("is not") as test:
                    with raises(AssertionError) as e:
                        assert 1 is not 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-is-not", encoder=snap)), error()

                with subsuite.test("in") as test:
                    with raises(AssertionError) as e:
                        assert 1 in [2], error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-in", encoder=snap)), error()

                with subsuite.test("not in") as test:
                    with raises(AssertionError) as e:
                        assert 1 not in [1], error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-not-in", encoder=snap)), error()

            with suite.test("common types") as subsuite:
                with subsuite.test("str") as test:
                    with raises(AssertionError) as e:
                        assert "hello" is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-str", encoder=snap)), error()

                with subsuite.test("list") as test:
                    with raises(AssertionError) as e:
                        assert [1] is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-list", encoder=snap)), error()

                with subsuite.test("tuple") as test:
                    with raises(AssertionError) as e:
                        assert (1,) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-tuple", encoder=snap)), error()

                with subsuite.test("dict") as test:
                    with raises(AssertionError) as e:
                        assert {'a':1} is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-dict", encoder=snap)), error()

                with subsuite.test("object type") as test:
                    with raises(AssertionError) as e:
                        assert object is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-object-type", encoder=snap)), error()

                with subsuite.test("object") as test:
                    with raises(AssertionError) as e:
                        assert object() is False, error()
                    test.note(e.exception)

                with subsuite.test("bytes") as test:
                    with raises(AssertionError) as e:
                        assert b'hello' is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-bytes", encoder=snap)), error()

                with subsuite.test("unicode") as test:
                    with raises(AssertionError) as e:
                        assert u'hello' is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-unicode", encoder=snap)), error()

            with suite.test("common idioms") as subsuite:
                with subsuite.test("if/else") as test:
                    with raises(AssertionError) as e:
                        assert (1 if 1 else 2) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-if-else", encoder=snap)), error()

                with subsuite.test("ellipsis") as test:
                    with raises(AssertionError) as e:
                        assert ... is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-ellipsis", encoder=snap)), error()

                with subsuite.test("assignment") as test:
                    def foo(x):
                        return x
                    with raises(AssertionError) as e:
                        assert foo(x = 1) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-assignment", encoder=snap)), error()

                with subsuite.test("subscript") as test:
                    with raises(AssertionError) as e:
                        assert [1,2,3][1:] is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-subscript", encoder=snap)), error()

                with subsuite.test("attr access") as test:
                    with raises(AssertionError) as e:
                        assert object().__class__ is False, error()
                    test.note(e.exception)

                with subsuite.test("attribute function call") as test:
                    with raises(AssertionError) as e:
                        assert "hello".join([' ', 'there']) is False, error()
                    test.note(e.exception)

                with subsuite.test("lambda name") as test:
                    with raises(AssertionError) as e:
                        assert (lambda x: x)(1) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-lambda-name", encoder=snap)), error()

                with subsuite.test("lambda expr") as test:
                    with raises(AssertionError) as e:
                        assert (lambda x: x+1)(1) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-lambda-expr", encoder=snap)), error()

                with subsuite.test("getitem") as test:
                    with raises(AssertionError) as e:
                        assert {'a':1}['a'] is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-getitem", encoder=snap)), error()

                with subsuite.test("generator expression") as test:
                    def foo(x):
                        return x
                    with raises(AssertionError) as e:
                        assert foo(x*x for x in range(2)) is False, error()
                    test.note(e.exception)

                with subsuite.test("list comprehension") as test:
                    def foo(x):
                        return x
                    with raises(AssertionError) as e:
                        assert foo([y*x for x in [[1],[2]] if len(x) > 0 for y in x if y > 0]) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-list-comprehension", encoder=snap)), error()

                with subsuite.test("set comprehension") as test:
                    with raises(AssertionError) as e, this() as that:
                        f = 5
                        assert {that(x) for x in range(f)} is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-set-comprehension", encoder=snap)), error()

                with subsuite.test("dict comprehension") as test:
                    with raises(AssertionError) as e, this() as that:
                        f, g = 2, 3
                        assert {that(x): x*f for x in range(g)} is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-dict-comprehension", encoder=snap)), error()

if main():
    with Test("regression") as regression:
        pass
