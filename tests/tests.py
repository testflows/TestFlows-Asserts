import sys
import re
import tempfile

from testflows.core import main
from testflows.core import Test as TestBase
from testflows.asserts import error, this, raises, snapshot 

class Test(TestBase):
    def run(self):
        with self.test("helpers") as suite:
            with suite.test("raises") as subsuite:
                with subsuite.test("not raised") as test:
                    with raises(AssertionError) as e:
                        with raises(AssertionError):
                            pass
                    test.note(e.exception)
                    assert snapshot(e.exception, "raises-not-raised", encoder=str)

                with subsuite.test("unexpected exception") as test:
                    with raises(AssertionError) as e:
                        with raises(AssertionError):
                            raise ValueError("error")
                    test.note(e.exception)
                    assert snapshot(e.exception, "raises-unexpected-exception", encoder=str)
                
                with subsuite.test("ok") as test:
                    with raises(ValueError) as e:
                        raise ValueError("error")
                    test.note(e.exception)
                    assert snapshot(e.exception, "raised-ok", encoder=str)

        with self.test("assertions") as suite:
            with suite.test("multiline") as subsuite:
                with subsuite.test("implicit") as test:
                    with raises(AssertionError) as e:
                        assert (1,
                                2) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "multiline-implicit", encoder=str)), error()

                with suite.test("explicit") as test:
                    with raises(AssertionError) as e:
                        assert "hello" == "foo bar"\
                            and 3 == 3\
                            and 1 > 1 or 1>1 or 3>3 or 4>+4, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "multiline-explicit", encoder=str)), error()

            with suite.test("this") as subsuite:
                with subsuite.test("assert with file read") as test:
                    with tempfile.TemporaryFile("w+") as fp:
                        fp.write("hello")
                        fp.seek(0)    
                        with raises(AssertionError) as e, this() as that:
                            assert not that(fp.read()), error()
                        test.note(e.exception)
                        with this() as that:
                            assert that(snapshot(e.exception, "this-assert_with_file_read", encoder=str)), error()

                with subsuite.test("assert with list append") as test:
                    some_list = []
                    with raises(AssertionError) as e, this() as that:
                        assert that(some_list.append(2)) == [1], error()
                    test.note(e.exception)
                    with test.test("assert that list did not change"):
                        assert some_list == [2], error()
                    with this() as that:
                        assert that(snapshot(e.exception, "this-assert_with_list_append", encoder=str)), error()

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
                            assert that(snapshot(e.exception, "func-args", encoder=str)), error()
            
                with subsuite.test("*args") as test:
                    vs = []
                    def foo(*x):
                        test.note(x)
                        vs.append(x)
                        return x
                    with raises(AssertionError) as e:
                        assert foo(*[1,2]) is False, error()
                    test.note(e.exception)
                    with test.test("assert *args are the same"):
                        assert vs[0] == vs[1]
                    with this() as that:
                        assert that(snapshot(e.exception, "func-*args", encoder=str)), error()

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
                        assert that(snapshot(e.exception, "func-**kwargs", encoder=str)), error()

                with subsuite.test("args *args **kwargs") as test:
                    vs = []
                    def foo(x,*y,**z):
                        test.note((x, y, z))
                        vs.append((x, y, z))
                        return x, y, z
                    with raises(AssertionError) as e:
                        assert foo(1,*[2],z=3) is False, error()
                    test.note(e.exception)
                    with test.test("assert args, *args, **kwargs are the same"):
                        assert vs[0] == vs[1]
                    with this() as that:
                        assert that(snapshot(e.exception, "func-args_*args_**kwargs", encoder=str)), error()

            with suite.test("boolean ops") as subsuite:
                with subsuite.test("and") as test:
                    with raises(AssertionError) as e:
                        assert 1 and 0, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-and", encoder=str)), error()

                with subsuite.test("multiple and") as test:
                    with raises(AssertionError) as e:
                        assert 1 and 2 and 3 and 0, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-multiple-and", encoder=str)), error()

                with subsuite.test("or") as test:
                    with raises(AssertionError) as e:
                        assert 0 or '', error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-or", encoder=str)), error()
                
                with subsuite.test("multiple or") as test:
                    with raises(AssertionError) as e:
                        assert 0 or '' or False or None, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "boolean-ops-multiple-or", encoder=str)), error()

            with suite.test("binary ops") as subsuite:
                with subsuite.test("add") as test:
                    with raises(AssertionError) as e:
                        assert 1 + 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-add", encoder=str)), error()
                
                with subsuite.test("sub") as test:
                    with raises(AssertionError) as e:
                        assert 1 - 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-sub", encoder=str)), error()
            
                with subsuite.test("mul") as test:
                    with raises(AssertionError) as e:
                        assert 1 * 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-mul", encoder=str)), error()

                with subsuite.test("div") as test:
                    with raises(AssertionError) as e:
                        assert 1 / 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-div", encoder=str)), error()

                with subsuite.test("mod") as test:
                    with raises(AssertionError) as e:
                        assert 1 % 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-mod", encoder=str)), error()

                with subsuite.test("pow") as test:
                    with raises(AssertionError) as e:
                        assert 1 ** 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-pow", encoder=str)), error()

                with subsuite.test("lshift") as test:
                    with raises(AssertionError) as e:
                        assert 1 << 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-lshift", encoder=str)), error()

                with subsuite.test("rshift") as test:
                    with raises(AssertionError) as e:
                        assert 1 >> 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-rshift", encoder=str)), error()

                with subsuite.test("bitOr") as test:
                    with raises(AssertionError) as e:
                        assert 1 | 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-bitOr", encoder=str)), error()

                with subsuite.test("bitXor") as test:
                    with raises(AssertionError) as e:
                        assert 1 ^ 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-bitXor", encoder=str)), error()
                
                with subsuite.test("bitAnd") as test:
                    with raises(AssertionError) as e:
                        assert 1 & 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-bitAnd", encoder=str)), error()

                with subsuite.test("floor div") as test:
                    with raises(AssertionError) as e:
                        assert 1 // 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-floor-div", encoder=str)), error()
                
                with subsuite.test("mixed ops") as test:
                    with raises(AssertionError) as e:
                        assert 1 + 3 - 4 * 5 ** 1 >> 1 << 3 % 5 | 2 ^ 5 & 6 // 3 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "binary-ops-mixed-ops", encoder=str)), error()

            with suite.test("unary ops") as subsuite:
                with subsuite.test("invert") as test:
                    with raises(AssertionError) as e:
                        assert ~4 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-invert", encoder=str)), error()

                with subsuite.test("not") as test:
                    with raises(AssertionError) as e:
                        assert not 4 is 4, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-not", encoder=str)), error()

                with subsuite.test("uadd") as test:
                    with raises(AssertionError) as e:
                        assert +4 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-uadd", encoder=str)), error()

                with subsuite.test("usub") as test:
                    with raises(AssertionError) as e:
                        assert -4 is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "unary-ops-usub", encoder=str)), error()

            with suite.test("compare ops") as subsuite:
                with subsuite.test("eq") as test:
                    with raises(AssertionError) as e:
                        assert 1 == 2, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-eq", encoder=str)), error()

                with subsuite.test("ne") as test:
                    with raises(AssertionError) as e:
                        assert 1 != 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-ne", encoder=str)), error()
                
                with subsuite.test("lt") as test:
                    with raises(AssertionError) as e:
                        assert 1 < 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-lt", encoder=str)), error()
                
                with subsuite.test("le") as test:
                    with raises(AssertionError) as e:
                        assert 1 <= 0, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-le", encoder=str)), error()
                
                with subsuite.test("gt") as test:
                    with raises(AssertionError) as e:
                        assert 1 > 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-gt", encoder=str)), error()
                
                with subsuite.test("ge") as test:
                    with raises(AssertionError) as e:
                        assert 1 >= 2, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-ge", encoder=str)), error()
                
                with subsuite.test("is") as test:
                    with raises(AssertionError) as e:
                        assert 1 is 2, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-is", encoder=str)), error()
                
                with subsuite.test("is not") as test:
                    with raises(AssertionError) as e:
                        assert 1 is not 1, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-is-not", encoder=str)), error()
                
                with subsuite.test("in") as test:
                    with raises(AssertionError) as e:
                        assert 1 in [2], error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-in", encoder=str)), error()
                
                with subsuite.test("not in") as test:
                    with raises(AssertionError) as e:
                        assert 1 not in [1], error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "compare-ops-not-in", encoder=str)), error()
            
            with suite.test("common types") as subsuite:
                with subsuite.test("str") as test:
                    with raises(AssertionError) as e:
                        assert "hello" is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-str", encoder=str)), error()
                
                with subsuite.test("list") as test:
                    with raises(AssertionError) as e:
                        assert [1] is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-list", encoder=str)), error()

                with subsuite.test("tuple") as test:
                    with raises(AssertionError) as e:
                        assert (1,) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-tuple", encoder=str)), error()
                
                with subsuite.test("dict") as test:
                    with raises(AssertionError) as e:
                        assert {'a':1} is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-dict", encoder=str)), error()
                
                with subsuite.test("object type") as test:
                    with raises(AssertionError) as e:
                        assert object is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-object-type", encoder=str)), error()
                
                with subsuite.test("object") as test:
                    with raises(AssertionError) as e:
                        assert object() is False, error()
                    test.note(e.exception)
                
                with subsuite.test("bytes") as test:
                    with raises(AssertionError) as e:
                        assert b'hello' is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-bytes", encoder=str)), error()
                
                with subsuite.test("unicode") as test:
                    with raises(AssertionError) as e:
                        assert u'hello' is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-types-unicode", encoder=str)), error()

            with suite.test("common idioms") as subsuite:
                with subsuite.test("if/else") as test:
                    with raises(AssertionError) as e:
                        assert (1 if 1 else 2) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-if-else", encoder=str)), error()
                
                with subsuite.test("ellipsis") as test:
                    with raises(AssertionError) as e:
                        assert ... is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-ellipsis", encoder=str)), error()
                
                with subsuite.test("assignment") as test:
                    def foo(x):
                        return x
                    with raises(AssertionError) as e:
                        assert foo(x = 1) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-assignment", encoder=str)), error()
                
                with subsuite.test("subscript") as test:
                    with raises(AssertionError) as e:
                        assert [1,2,3][1:] is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-subscript", encoder=str)), error()
                
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
                        assert that(snapshot(e.exception, "common-idioms-lambda-name", encoder=str)), error()

                with subsuite.test("lambda expr") as test:
                    with raises(AssertionError) as e:
                        assert (lambda x: x+1)(1) is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-lambda-expr", encoder=str)), error()

                with subsuite.test("getitem") as test:
                    with raises(AssertionError) as e:
                        assert {'a':1}['a'] is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-getitem", encoder=str)), error()

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
                        assert that(snapshot(e.exception, "common-idioms-list-comprehension", encoder=str)), error()

                with subsuite.test("set comprehension") as test:
                    with raises(AssertionError) as e, this() as that:
                        f = 5
                        assert {that(x) for x in range(f)} is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-set-comprehension", encoder=str)), error()

                with subsuite.test("dict comprehension") as test:
                    with raises(AssertionError) as e, this() as that:
                        f, g = 2, 3
                        assert {that(x): x*f for x in range(g)} is False, error()
                    test.note(e.exception)
                    with this() as that:
                        assert that(snapshot(e.exception, "common-idioms-dict-comprehension", encoder=str)), error()

if main():
    with Test("regression") as regression:
        pass
