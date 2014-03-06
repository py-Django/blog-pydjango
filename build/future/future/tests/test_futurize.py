# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import pprint
import tempfile
from subprocess import Popen, PIPE
import os

from future.tests.base import CodeHandler, unittest, skip26


class TestFuturizeSimple(CodeHandler):
    """
    This class contains snippets of Python 2 code (invalid Python 3) and
    tests for whether they can be passed to ``futurize`` and immediately
    run under both Python 2 again and Python 3.
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp() + os.path.sep
        super(TestFuturizeSimple, self).setUp()

    @unittest.expectedFailure
    def test_problematic_string(self):
        """ This string generates a SyntaxError on Python 3 unless it has
        an r prefix.
        """
        before = r"""
        s = 'The folder is "C:\Users"'.
        """
        after = r"""
        s = r'The folder is "C:\Users"'.
        """
        self.convert_check(before, after)

    def test_tobytes(self):
        """
        The --tobytes option converts all UNADORNED string literals 'abcd' to b'abcd'.
        It does apply to multi-line strings but doesn't apply if it's a raw
        string, because ur'abcd' is a SyntaxError on Python 2 and br'abcd' is a
        SyntaxError on Python 3.
        """
        before = r"""
        s0 = '1234'
        s1 = '''5678
        '''
        s2 = "9abc"
        # Unchanged:
        s3 = r'1234'
        s4 = R"defg"
        s5 = u'hijk'
        s6 = u"lmno"
        s7 = b'lmno'
        s8 = b"pqrs"
        """
        after = r"""
        s0 = b'1234'
        s1 = b'''5678
        '''
        s2 = b"9abc"
        # Unchanged:
        s3 = r'1234'
        s4 = R"defg"
        s5 = u'hijk'
        s6 = u"lmno"
        s7 = b'lmno'
        s8 = b"pqrs"
        """
        self.convert_check(before, after, tobytes=True)

    @unittest.expectedFailure
    def test_izip(self):
        before = """
        from itertools import izip
        for (a, b) in izip([1, 3, 5], [2, 4, 6]):
            pass
        """
        after = """
        from future.builtins import zip
        for (a, b) in zip([1, 3, 5], [2, 4, 6]):
            pass
        """
        self.convert_check(before, after, stages=(1, 2), ignore_imports=False)

    def test_UserList(self):
        before = """
        from UserList import UserList
        a = UserList([1, 3, 5])
        assert len(a) == 3
        """
        after = """
        from collections import UserList
        a = UserList([1, 3, 5])
        assert len(a) == 3
        """
        self.convert_check(before, after, stages=(1, 2), ignore_imports=True)

    @unittest.expectedFailure
    def test_no_unneeded_list_calls(self):
        """
        TODO: get this working
        """
        code = """
        for (a, b) in zip(range(3), range(3, 6)):
            pass
        """
        self.unchanged(code)

    @unittest.expectedFailure
    def test_import_builtins(self):
        before = """
        a = raw_input()
        b = open(a, b, c)
        c = filter(a, b)
        d = map(a, b)
        e = isinstance(a, str)
        f = bytes(a, encoding='utf-8')
        for g in xrange(10**10):
            pass
        h = reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
        super(MyClass, self)
        """
        after = """
        from future.builtins import bytes
        from future.builtins import filter
        from future.builtins import input
        from future.builtins import map
        from future.builtins import open
        from future.builtins import range
        from future.builtins import super
        from functools import reduce
        a = input()
        b = open(a, b, c)
        c = list(filter(a, b))
        d = list(map(a, b))
        e = isinstance(a, str)
        f = bytes(a, encoding='utf-8')
        for g in range(10**10):
            pass
        h = reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
        super(MyClass, self)
        """
        self.convert_check(before, after, ignore_imports=False, run=False)

    def test_xrange(self):
        code = '''
        for i in xrange(10):
            pass
        '''
        self.convert(code)
    
    @skip26
    @unittest.expectedFailure
    def test_source_coding_utf8(self):
        """
        Tests to ensure that the source coding line is not corrupted or
        removed. It must be left as the first line in the file (including
        before any __future__ imports). Also tests whether the unicode
        characters in this encoding are parsed correctly and left alone.
        """
        code = """
        # -*- coding: utf-8 -*-
        icons = [u"◐", u"◓", u"◑", u"◒"]
        """
        self.unchanged(code)

    def test_exception_syntax(self):
        """
        Test of whether futurize handles the old-style exception syntax
        """
        before = """
        try:
            pass
        except IOError, e:
            val = e.errno
        """
        after = """
        try:
            pass
        except IOError as e:
            val = e.errno
        """
        self.convert_check(before, after)

    def test_super(self):
        """
        This tests whether futurize keeps the old two-argument super() calls the
        same as before. It should, because this still works in Py3.
        """
        code = '''
        class VerboseList(list):
            def append(self, item):
                print('Adding an item')
                super(VerboseList, self).append(item)
        '''
        self.unchanged(code)

    @unittest.expectedFailure
    def test_file(self):
        """
        file() as a synonym for open() is obsolete and invalid on Python 3.
        """
        before = '''
        f = file(__file__)
        data = f.read()
        f.close()
        '''
        after = '''
        f = open(__file__)
        data = f.read()
        f.close()
        '''
        self.convert_check(before, after)

    def test_apply(self):
        before = '''
        def addup(*x):
            return sum(x)
        
        assert apply(addup, (10,20)) == 30
        '''
        after = """
        def addup(*x):
            return sum(x)
        
        assert addup(*(10,20)) == 30
        """
        self.convert_check(before, after)
    
    @unittest.skip('not implemented yet')
    def test_download_pypi_package_and_test(self, package_name='future'):
        URL = 'http://pypi.python.org/pypi/{0}/json'
        
        import requests
        r = requests.get(URL.format(package_name))
        pprint.pprint(r.json())
        
        download_url = r.json()['urls'][0]['url']
        filename = r.json()['urls'][0]['filename']
        # r2 = requests.get(download_url)
        # with open('/tmp/' + filename, 'w') as tarball:
        #     tarball.write(r2.content)

    @unittest.expectedFailure
    def test_raw_input(self):
        """
        Passes in a string to the waiting input() after futurize
        conversion.

        The code is the first snippet from these docs:
            http://docs.python.org/2/library/2to3.html
        """
        before = """
        from io import BytesIO
        def greet(name):
            print "Hello, {0}!".format(name)
        print "What's your name?"
        import sys
        oldstdin = sys.stdin

        sys.stdin = BytesIO(b'Ed\\n')
        name = raw_input()
        greet(name.decode())

        sys.stdin = oldstdin
        assert name == b'Ed'
        """
        desired = """
        from io import BytesIO
        def greet(name):
            print("Hello, {0}!".format(name))
        print("What's your name?")
        import sys
        oldstdin = sys.stdin

        sys.stdin = BytesIO(b'Ed\\n')
        name = input()
        greet(name.decode())

        sys.stdin = oldstdin
        assert name == b'Ed'
        """
        self.convert_check(before, desired, run=False)

        for interpreter in self.interpreters:
            p1 = Popen([interpreter, self.tempdir + 'mytestscript.py'],
                       stdout=PIPE, stdin=PIPE, stderr=PIPE, env=self.env)
            (stdout, stderr) = p1.communicate(b'Ed')
            self.assertEqual(stderr, b'')
            self.assertEqual(stdout, b"What's your name?\nHello, Ed!\n")

    def test_literal_prefixes_are_not_stripped(self):
        """
        Tests to ensure that the u'' and b'' prefixes on unicode strings and
        byte strings are not removed by the futurize script.  Removing the
        prefixes on Py3.3+ is unnecessary and loses some information -- namely,
        that the strings have explicitly been marked as unicode or bytes,
        rather than just e.g. a guess by some automated tool about what they
        are.
        """
        code = '''
        s = u'unicode string'
        b = b'byte string'
        '''
        self.unchanged(code)

    @unittest.expectedFailure
    def test_division(self):
        """
        TODO: implement this!
        """
        before = """
        x = 1 / 2
        """
        after = """
        from future.utils import old_div
        x = old_div(1, 2)
        """
        self.convert_check(before, after, stages=[1])


class TestFuturizeRenamedStdlib(CodeHandler):
    def test_renamed_modules(self):
        before = """
        import ConfigParser
        import copy_reg
        import cPickle
        import cStringIO
        """
        after = """
        import configparser
        import copyreg
        import pickle
        import io
        """
        self.convert_check(before, after)
    
    @unittest.expectedFailure
    def test_urllib_refactor(self):
        # Code like this using urllib is refactored by futurize --stage2 to use
        # the new Py3 module names, but ``future`` doesn't support urllib yet.
        before = """
        import urllib

        URL = 'http://pypi.python.org/pypi/future/json'
        package_name = 'future'
        r = urllib.urlopen(URL.format(package_name))
        data = r.read()
        """
        after = """
        import urllib.request
        
        URL = 'http://pypi.python.org/pypi/future/json'
        package_name = 'future'
        r = urllib.request.urlopen(URL.format(package_name))
        data = r.read()
        """
        self.convert_check(before, after)

    def test_renamed_copy_reg_and_cPickle_modules(self):
        """
        Example from docs.python.org/2/library/copy_reg.html
        """
        before = """
        import copy_reg
        import copy
        import cPickle
        class C(object):
            def __init__(self, a):
                self.a = a

        def pickle_c(c):
            print('pickling a C instance...')
            return C, (c.a,)

        copy_reg.pickle(C, pickle_c)
        c = C(1)
        d = copy.copy(c)
        p = cPickle.dumps(c)
        """
        after = """
        import copyreg
        import copy
        import pickle
        class C(object):
            def __init__(self, a):
                self.a = a

        def pickle_c(c):
            print('pickling a C instance...')
            return C, (c.a,)

        copyreg.pickle(C, pickle_c)
        c = C(1)
        d = copy.copy(c)
        p = pickle.dumps(c)
        """
        self.convert_check(before, after)

    @unittest.expectedFailure
    def test_Py2_StringIO_module(self):
        """
        This requires that the argument to io.StringIO be made a
        unicode string explicitly if we're not using unicode_literals:

        Ideally, there would be a fixer for this. For now:

        TODO: add the Py3 equivalent for this to the docs. Also add back
        a test for the unicode_literals case.
        """
        before = """
        import cStringIO
        import StringIO
        s1 = cStringIO.StringIO('my string')
        s2 = StringIO.StringIO('my other string')
        assert isinstance(s1, cStringIO.InputType)
        """

        # There is no io.InputType in Python 3. futurize should change this to
        # something like this. But note that the input to io.StringIO
        # must be a unicode string on both Py2 and Py3.
        after = """
        import io
        import io
        s1 = io.StringIO(u'my string')
        s2 = io.StringIO(u'my other string')
        assert isinstance(s1, io.StringIO)
        """
        self.convert_check(before, after)


class TestFuturizeStage1(CodeHandler):
    """
    Tests "stage 1": safe optimizations: modernizing Python 2 code so that it
    uses print functions, new-style exception syntax, etc.

    The behaviour should not change and this should introduce no dependency on
    the ``future`` package. It produces more modern Python 2-only code. The
    goal is to reduce the size of the real porting patch-set by performing
    the uncontroversial patches first.
    """

    def test_apply(self):
        """
        apply() should be changed by futurize --stage1
        """
        before = '''
        def f(a, b):
            return a + b

        args = (1, 2)
        assert apply(f, args) == 3
        assert apply(f, ('a', 'b')) == 'ab'
        '''
        after = '''
        def f(a, b):
            return a + b

        args = (1, 2)
        assert f(*args) == 3
        assert f(*('a', 'b')) == 'ab'
        '''
        self.convert_check(before, after, stages=[1])

    def test_xrange(self):
        """
        xrange should not be changed by futurize --stage1
        """
        code = '''
        for i in xrange(10):
            pass
        '''
        self.unchanged(code, stages=[1])

    @unittest.expectedFailure
    def test_absolute_import_changes(self):
        """
        Implicit relative imports should be converted to absolute or explicit
        relative imports correctly.

        Issue #16 (with porting bokeh/bbmodel.py)
        """
        with open(tempdir + 'specialmodels.py', 'w') as f:
            f.write('pass')

        before = """
        import specialmodels.pandasmodel
        specialmodels.pandasmodel.blah()
        """
        after = """
        from __future__ import absolute_import
        from .specialmodels import pandasmodel
        pandasmodel.blah()
        """
        self.convert_check(before, after, stages=[1])

    def test_safe_futurize_imports(self):
        """
        The standard library module names should not be changed until stage 2
        """
        before = """
        import ConfigParser
        import HTMLParser
        import collections

        ConfigParser.ConfigParser
        HTMLParser.HTMLParser
        d = collections.OrderedDict()
        """
        self.unchanged(before, stages=[1])

    def test_print(self):
        before = """
        print 'Hello'
        """
        after = """
        print('Hello')
        """
        self.convert_check(before, after, stages=[1])

        before = """
        import sys
        print >> sys.stderr, 'Hello', 'world'
        """
        after = """
        import sys
        print('Hello', 'world', file=sys.stderr)
        """
        self.convert_check(before, after, stages=[1])

    def test_print_already_function(self):
        """
        Running futurize --stage1 should not add a second set of parentheses 
        """
        before = """
        print('Hello')
        """
        self.unchanged(before, stages=[1])

    @unittest.expectedFailure
    def test_print_already_function_complex(self):
        """
        Running futurize --stage1 does add a second second set of parentheses
        in this case. This is because the underlying lib2to3 has two distinct
        grammars -- with a print statement and with a print function -- and,
        when going forwards (2 to both), futurize assumes print is a statement,
        which raises a ParseError.
        """
        before = """
        import sys
        print('Hello', 'world', file=sys.stderr)
        """
        self.unchanged(before, stages=[1])

    def test_exceptions(self):
        before = """
        try:
            raise AttributeError('blah')
        except AttributeError, e:
            pass
        """
        after = """
        try:
            raise AttributeError('blah')
        except AttributeError as e:
            pass
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_string_exceptions(self):
        """
        2to3 does not convert string exceptions: see
        http://python3porting.com/differences.html.
        """
        before = """
        try:
            raise "old string exception"
        except Exception, e:
            pass
        """
        after = """
        try:
            raise Exception("old string exception")
        except Exception as e:
            pass
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_oldstyle_classes(self):
        """
        We don't convert old-style classes to new-style automatically. Should we?
        """
        before = """
        class Blah:
            pass
        """
        after = """
        class Blah(object):
            pass
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_all(self):
        """
        Standard library module names should not be changed in stage 1
        """
        before = """
        import ConfigParser
        import HTMLParser
        import collections

        print 'Hello'
        try:
            raise AttributeError('blah')
        except AttributeError, e:
            pass
        print 'Number is', 1 / 2
        """
        after = """
        from future.utils import old_div
        import Configparser
        import HTMLParser
        import collections

        print('Hello')
        try:
            raise AttributeError('blah')
        except AttributeError as e:
            pass
        print('Number is', old_div(1, 2))
        """
        self.convert_check(before, after, stages=[1])
        
    def test_octal_literals(self):
        before = """
        mode = 0644
        """
        after = """
        mode = 0o644
        """
        self.convert_check(before, after)

    def test_long_int_literals(self):
        before = """
        bignumber = 12345678901234567890L
        """
        after = """
        bignumber = 12345678901234567890
        """
        self.convert_check(before, after)

    def test___future___import_position(self):
        """
        Issue #4: __future__ imports inserted too low in file: SyntaxError
        """
        code = """
        # Comments here
        # and here
        __version__=''' $Id$ '''
        __doc__="A Sequencer class counts things. It aids numbering and formatting lists."
        __all__='Sequencer getSequencer setSequencer'.split()
        #
        # another comment
        #
        
        CONSTANTS = [ 0, 01, 011, 0111, 012, 02, 021, 0211, 02111, 013 ]
        _RN_LETTERS = "IVXLCDM"
        
        def my_func(value):
            pass
        
        ''' Docstring-like comment here '''
        """
        self.convert(code)


if __name__ == '__main__':
    unittest.main()
