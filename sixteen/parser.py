# -*- coding: utf-8 -*-

import re
from functools import wraps, partial


class _meta_parser(type):
    def __init__(cls, name, bases, dictionary):
        # make sure each subclass of the Parser has its own empty "_by_name",
        # "preprocessors", and "registered" attributes.
        cls._by_name = {}
        cls.registered = []
        cls.translators = []
        cls.preprocessors = []
        #TODO: inherit these.
        type.__init__(cls, name, bases, dictionary)


class Parser(object):
    __metaclass__ = _meta_parser
        
    @classmethod
    def register(cls, pattern):
        """This is a function that, given a regular expression pattern, returns
        a decorator that registers its decorated function as a parse function
        for this parser and wraps it in a function that raises Defer if the
        pattern doesn't match.
        """
        def parse_function_decorator(fn):
            "This is a decorator that registers a parse function."

            @wraps(fn)
            def parse_function_wrapper(self, word, **kwargs):
                # check the match.
                match = re.match(pattern, word)
                # if it matches, try running the function with the groups
                if match:
                    return fn(self, *match.groups(), **kwargs)
                # if it doesn't, raise a Defer so that the parser knows to
                # keep trying other things.
                else:
                    raise Defer()

            # save this thing in a dict by its name and in an ordered list
            cls._by_name[fn.__name__] = parse_function_wrapper
            cls.registered.append(parse_function_wrapper)
            return parse_function_wrapper

        return parse_function_decorator

    @classmethod
    def preprocess(cls, fn):
        "A decorator that registers its decorated function as a preprocessor."
        cls.preprocessors.append(fn)

    @classmethod
    def translator(cls, fn):
        "Register a function that translates the AST into whatever output."
        cls.translators.append(fn)

    def parse(self, word):
        "Try each registered parse function in turn to find one that matches."
        # run each preprocessor on the input, first.
        for preprocess in self.preprocessors:
            word = preprocess(self, word)

        for method in self.registered:
            try:
                return method(self, word)
            except Defer:
                # if the parse function raises a Defer, skip it but keep going
                continue
        else:
            # if nothing matches, raise a ParserError with the word.
            raise ParserError(word)

    def __getattr__(self, name):
        """Address any given parse function like any other instance method, and
        pass it self.
        """
        return partial(self._by_name[name], self)

    def parse_tree(self, iterable):
        "Parse an iterable into a tree and run all of the translators on it."
        tree = [self.parse(i) for i in iterable]
        for translate in self.translators:
            tree = translate(self, tree)
        return tree

 
class ParserError(Exception):
    "Oh no, we don't know how to parse this thing."
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Defer(Exception):
    """Raise this error if this parsing function doesn't know how to parse some
    thing, but it's possible for some other function to parse it.
    """
    pass
