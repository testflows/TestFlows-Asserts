# Copyright 2019 Vitaliy Zakaznikov, TestFlows Test Framework
#
#      http://testflows.com
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
import ast
import copy
import inspect
import textwrap
import linecache
import builtins

__all__ = ["error", "this"]

class this(object):
    """Obtains value so that expression
    does not need to be reinterpreted if 
    assertion fails.
    """
    __slots__ = ("stack",)
    def __init__(self):
        self.stack = []

    def __enter__(self):
        return self

    def __call__(self, x):
        self.stack.append(x)
        return x

    def __exit__(self, *args):
        pass


class AssertEval(ast.NodeVisitor):
    """Asssertion expression evaluator.
    
    :param frame: frame where the assertion occured
    """
    # Known types
    _simple = (
        ast.Num, 
        ast.Str,
        ast.NameConstant,
        ast.Attribute,
        ast.Call,
        ast.BinOp,
        ast.UnaryOp,
        ast.IfExp,
        ast.BoolOp,
        ast.List,
        ast.Tuple,
        ast.Set,
        ast.Dict,
        ast.Starred,
        ast.Compare,
     )
    
    # operator symbols
    _op_symbols = {
        # boolean ops
        ast.And: "and",
        ast.Or: "or",
        # binary ops
        ast.Add: "+",
        ast.Sub: "-",
        ast.Mult: "*",
        ast.Div: "/",
        ast.Mod: "%",
        ast.Pow: "**",
        ast.LShift: "<<",
        ast.RShift: ">>",
        ast.BitOr: "|",
        ast.BitXor: "^",
        ast.BitAnd: "&",
        ast.FloorDiv: "//",
        # compare ops
        ast.Eq: "==",
        ast.NotEq: "!=",
        ast.Lt: "<",
        ast.LtE: "<=",
        ast.Gt: ">",
        ast.GtE: ">=",
        ast.Is: "is",
        ast.IsNot: "is not",
        ast.In: "in",
        ast.NotIn: "not in",
        # unary ops
        ast.Invert: "~",
        ast.Not: "not",
        ast.UAdd: "+",
        ast.USub: "-"
    }
    
    # boolean operators
    _boolean_ops = {
        ast.And: lambda left, right: left and right,
        ast.Or: lambda left, right: left or right
    }

    # binary operators
    _binary_ops = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right,
        ast.Mod: lambda left, right: left % right,
        ast.Pow: lambda left, right: left ** right,
        ast.LShift: lambda left, right: left << right,
        ast.RShift: lambda left, right: left >> right,
        ast.BitOr: lambda left, right: left | right,
        ast.BitXor: lambda left, right: left ^ right,
        ast.BitAnd: lambda left, right: left & right,
        ast.FloorDiv: lambda left, right: left // right
    }

    # unary operators
    _unary_ops = {
        ast.Invert: lambda operand: ~operand,
        ast.Not: lambda operand: not operand,
        ast.UAdd: lambda operand: +operand,
        ast.USub: lambda operand: -operand
    }
    
    # comparison operators
    _compare_ops = {
        ast.Eq: lambda left, right: left == right,
        ast.NotEq: lambda left, right: left != right,
        ast.Lt: lambda left, right: left < right,
        ast.LtE: lambda left, right: left <= right,
        ast.Gt: lambda left, right: left > right,
        ast.GtE: lambda left, right: left >= right,
        ast.Is: lambda left, right: left is right,
        ast.IsNot: lambda left, right: left is not right,
        ast.In: lambda left, right: left in right,
        ast.NotIn: lambda left, right: left not in right
    }
    
    class FuncResult(object):
        """Result wrapper.
        """
        def __init__(self, result):
            self.result = result
        
        def __repr__(self):
            return "= " + _saferepr(self.result)
    
    class CompareResult(object):
        """Compare result wrapper.
        """
        def __init__(self, result):
            self.result = result
        
        def __repr__(self):
            return "= " + _saferepr(self.result)   
    
    def __init__(self, frame):
        def error(desc=None):
            pass
        self.frame = frame
        self.f_globals = self.frame.f_globals
        self.f_locals = dict(self.frame.f_locals)
        self.f_locals['error'] = error
        self.nodes = []
        self._is_assert = False
        
    def eval(self):
        """Evaluate assert expression.
        """
        frame_info = inspect.getframeinfo(self.frame)
        code = frame_info.code_context[0].strip()
        
        expression = ""
        expression_ast = None
        sourcelines, startline = inspect.getsourcelines(self.frame)
        startline = max(1, startline)
        for i in range(frame_info.lineno - startline + 1, 0, -1):
            expression = sourcelines[i - 1] + expression
            try:
                self.expression = textwrap.dedent(expression).strip()
                expression_ast = ast.parse(self.expression)
                break
            except SyntaxError as e:
                pass
        self.expression = self.expression.split("\n")
        self.visit(expression_ast)
        return self.expression, self.nodes

    def _find_operator(self, op_type, lineno, col_offset):
        """Find an operator offset which is right before
        the specified line number and column offset.
        
        :param lineno: line number
        :param col_offset: column offset
        """
        expression = self.expression[:lineno]
        expression[-1] = expression[-1][:col_offset+1].rstrip("({[")
        op_sym = self._op_symbols.get(op_type, None)
        if op_sym is None:
            raise RuntimeError("unknown operator type '%s'" % op_type)
        for lineno, line in reversed(list(enumerate(expression, 1))):
            idx = line.rfind(op_sym)
            if idx >= 0:
                break
        # if we did not find the operator returns (1, -1)
        return lineno, idx

    def visit_Module(self, node):
        return self.visit(node.body[0])

    def visit_Expr(self, node):
        if not self._is_assert:
            raise RuntimeError("not called from the assert statement")
        return self.visit(node.value)

    def visit_Assert(self, node):
        self._is_assert = True
        result = bool(self.visit(node.test))
        self.nodes.append((result, node))
        return result

    def visit_Compare(self, node):
        result = self.visit(node.left)
        if not isinstance(node.left, self._simple): 
            self.nodes.append((result, node.left))
        for operator, comparator in zip(node.ops, node.comparators):
            op = type(operator)
            func = self._compare_ops[op]
            right = self.visit(comparator)
            result = func(result, right)
            if not isinstance(comparator, self._simple):
                self.nodes.append((right, comparator))
            _operator = copy.copy(operator)
            _operator.lineno, _operator.col_offset = self._find_operator(op, comparator.lineno, comparator.col_offset)
            self.nodes.append((self.FuncResult(result), _operator))
        return result

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        self.nodes.append((value, node))
        res = getattr(value, node.attr)
        self.nodes.append((self.FuncResult(res), node))
        return res

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
        else:
            name = self.visit(node.func)
        
        if callable(name):
            func = name
        elif name in self.f_locals:
            func = self.f_locals[name]
        elif name in self.f_globals:
            func = self.f_globals[name]
        elif getattr(builtins, name):
            func = getattr(builtins, name)
        else:
            raise NameError("Function '{}' is not defined".format(name),
                            node.lineno, node.col_offset)
        
        if isinstance(func, this):
            if (func.stack):
                result = func.stack.pop(0)
            else:
                result = None
            self.nodes.append((self.FuncResult(result), node))
            return result

        starred = []
        args = []
        for arg in node.args:
            if isinstance(arg, ast.AST):
                arg_value = self.visit(arg)
            if not isinstance(arg, self._simple):
                self.nodes.append((arg_value, arg)) 
            args.append(arg_value)

        if args and isinstance(args[-1], ast.Starred):
            starred = args.pop(-1).value

        keywords = {}
        for keyword in node.keywords:
            keyword_value = self.visit(keyword.value)
            keywords[keyword.arg] = keyword_value
            if not isinstance(keyword.value, self._simple):
                self.nodes.append((keyword_value, keyword.value))

        value = func(*args, *starred, **keywords)
        self.nodes.append((self.FuncResult(value), node))
        return value
   
    def visit_Starred(self, node):
        result = self.visit(node.value)
        return ast.Starred(result, node.ctx)

    def visit_BinOp(self, node):
        op = type(node.op)
        func = self._binary_ops[op]
        left = self.visit(node.left)
        if not isinstance(node.left, self._simple):
            self.nodes.append((left, node.left))
        right = self.visit(node.right)
        if not isinstance(node.right, self._simple):
            self.nodes.append((right, node.right))
        result = func(left, right)
        _operator = copy.copy(node.op)
        _operator.lineno, _operator.col_offset = self._find_operator(op, node.right.lineno, node.right.col_offset)
        self.nodes.append((self.FuncResult(result), _operator))
        return result

    def visit_UnaryOp(self, node):
        op = type(node.op)
        func = self._unary_ops[op]
        operand = self.visit(node.operand)
        if not isinstance(node.operand, self._simple):
            self.nodes.append((operand, node.operand))
        result = func(operand)
        self.nodes.append((self.FuncResult(result), node))
        return result

    def visit_IfExp(self, node):
        body = self.visit(node.body)
        if not isinstance(node.body, self._simple):
            self.nodes.append((body, node.body))
        test = self.visit(node.test)
        if not isinstance(node.test, self._simple):
            self.nodes.append((test, node.test))
        orelse = self.visit(node.orelse)
        if not isinstance(node.orelse, self._simple):
            self.nodes.append((orelse, node.orelse))
        result = body if test else orelse
        self.nodes.append((self.FuncResult(result), node))
        return result

    def visit_BoolOp(self, node):
        op = type(node.op)
        operator = node.op
        func = self._boolean_ops[op]
        
        left = self.visit(node.values[0])
        if not isinstance(node.values[0], self._simple):
            self.nodes.append((left, node.values[0]))
        
        for value in node.values[1:]:
            right = self.visit(value)
            if not isinstance(value, self._simple):
                self.nodes.append((right, value)) 
            result = func(left, right)
            _operator = copy.copy(operator)
            _operator.lineno, _operator.col_offset = self._find_operator(op, value.lineno, value.col_offset)
            self.nodes.append((self.FuncResult(result), _operator))
            left = result
        return result

    def visit_Tuple(self, node):
        result = []
        for e in node.elts:
            v = self.visit(e)
            if not isinstance(e, self._simple):
                self.nodes.append((v, e))
            result.append(v)
        result = tuple(result)
        self.nodes.append((self.FuncResult(result), node))
        return result

    def visit_Set(self, node):
        result = []
        for e in node.elts:
            v = self.visit(e)
            if not isinstance(e, self._simple):
                self.nodes.append((v, e))
            result.append(v)
        result = set(result)
        self.nodes.append((self.FuncResult(result), node))
        return result

    def visit_List(self, node):
        result = []
        for e in node.elts:
            v = self.visit(e)
            if not isinstance(e, self._simple):
                self.nodes.append((v, e))
            result.append(v)
        self.nodes.append((self.FuncResult(result), node))
        return result

    def visit_Dict(self, node):
        keys= []
        for k in node.keys:
            v = self.visit(k)
            if not isinstance(k, self._simple):
                self.nodes.append((v, k))
            keys.append(v)
        values = []
        for value in node.values:
            v = self.visit(value)
            if not isinstance(value, self._simple):
                self.nodes.append((v, value))
            values.append(v)
        result = dict(zip(keys, values))
        self.nodes.append((self.FuncResult(result), node))
        return result

    def generic_visit(self, node):
        # some expressions like comprehensions will have their 
        # own local scope so therefore we combine globals and locals
        # scopes into one globals scope
        f_globals = self.f_globals.copy()
        f_globals.update(self.f_locals)
        if isinstance(node, ast.expr):
            bytecode = compile(ast.Expression(node), "assertion node", "eval")
            return eval(bytecode, f_globals)
        elif isinstance(node, ast.stmt):
            bytecode = compile(ast.Module([node]), "assertion node", "exec")
            return exec(bytecode, f_globals)
        return super(AssertEval, self).generic_visit(node)

def _code_block(filename, lineno, before=8, after=4):
    """Retrieve code blocks around a given line
    inside the source.
    
    :param filename: name of the source file
    :param lineno: line number
    :param before: number of lines before the line number
    :param after: number of line after the line number
    """
    min_n = max(lineno - before, 0)
    max_n = lineno + after
    
    line_fmt = "%" + str(len(str(max_n))) + "d|  %s"
    lines = []
    
    for n in range(min_n, max_n):
        line = linecache.getline(filename, n)
        if n > min_n and len(line) == 0:
            break
        print_line = line_fmt % (n, line)
        if n == lineno:
            print_line = "|> ".join(print_line.split("|  ", 1))
        lines.append(print_line)
    
    return lines


class error(object):
    """Error object that generates a descriptive 
    error message when assert fails.
    
    :param desc: description, default: `None`
    :param frame: frame, default: `None`
    :param frame_info: frame info, default: `None`
    :param expression: expression, default: `None`
    :param nodes: a list of expression value nodes, default: `None`
    """
    def __init__(self, desc=None, frame=None, frame_info=None, expression=None, nodes=None):
        self.frame = frame
        if self.frame is None:
            self.frame = inspect.currentframe().f_back
        self.frame_info = frame_info
        if self.frame_info is None:
            self.frame_info = inspect.getframeinfo(self.frame)
        self.desc = str(desc) if desc is not None else None
        self.nodes = list(nodes) if nodes is not None else None
        self.expression = str(expression) if expression is not None else None
        self.message = self.generate()

    def __str__(self):
        return self.message

    def generate(self):
        """Re-evaluate assertion statement and 
        generate an error message.
        """
        if self.nodes is None:
            self.expression, self.nodes = AssertEval(self.frame).eval()
        return self.generate_message()

    def generate_message(self):
        """Generate an error message.
        
        :param expression: expression
        :param frame_info: frame info
        """
        frame_info = self.frame_info
        
        message = "Oops! Assertion failed"
        if self.expression:
            message += "\n\nThe following assertion was not satisfied"
            for line in self.expression:
                message += "\n  " + line

        if self.desc:
            message += "\n\nDescription"
            message += "\n  " + self.desc[0].capitalize() + self.desc[1:]
        
        if self.nodes:
            message += "\n\nAssertion values"
            for v, n in self.nodes:
                for i, line in enumerate(self.expression):
                    message += "\n  " + line
                    if n.lineno == i + 1:
                        col_offset = n.col_offset
                        if col_offset < 0:
                            col_offset = len(line) - len(line.lstrip())
                        message += "\n  " + " " * col_offset + "^ is " + _saferepr(v)
        
        message += "\n\nWhere"
        message += "\n  File '%s', line %d in '%s'" % (frame_info.filename, 
            frame_info.lineno, frame_info.function)

        message += "\n\n" + "".join(self.code_block(frame_info.filename, frame_info.lineno))

        return message        

    def code_block(self, filename, lineno, before=8, after=4):
        """Retrieve code blocks around a given line
        inside the source.
        
        :param filename: name of the source file
        :param lineno: line number
        :param before: number of lines before the line number
        :param after: number of line after the line number
        """
        min_n = max(lineno - before, 0)
        max_n = lineno + after
        
        line_fmt = "%" + str(len(str(max_n))) + "d|  %s"
        lines = []
        
        for n in range(min_n, max_n):
            line = linecache.getline(filename, n)
            if n > min_n and len(line) == 0:
                break
            print_line = line_fmt % (n, line)
            if n == lineno:
                print_line = "|> ".join(print_line.split("|  ", 1))
            lines.append(print_line)
        
        return lines


def _saferepr(value):
    try:
        r = textwrap.indent(repr(value), " " * 2)
        return r.lstrip()
    except Exception as e:
        return "<unknown> (repr() failed with '%s')" % str(e)
