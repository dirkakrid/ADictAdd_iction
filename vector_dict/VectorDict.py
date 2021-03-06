#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Dict on steroids """
from collections import namedtuple, defaultdict
from collections import Sequence, Mapping
from math import sqrt
import types
from  Clause import Clause, is_leaf, is_container, is_function
from Operator import Adder,Subber
#WTFPL

__all__ = ['cos', 'dot',  'iter_object' , 'tree_from_path', 'Path',
    'flattening', 'can_be_walked', 'Element', 'flatten_generator']



def convert_tree(a_tree, defaultdict_factory = int):
    """
    convert from any other nested object to a VectorDict 
    espaecially usefull for constructing a vector dict from 
    intricated dict of dicts. 
    *Dont work as a class method (why ?)*

 >>> convert_tree({ 'a' : { 'a' : { 'r' : "yop", 'b' : { 'c' :  1 }}}}).tprint()
 {
     a : {
         a : {
             r : 'yop',
             b : {
                 c : 1,
             },
         },
     },
 }

    ** BUG : if empty dict is a leaf, default_factory is not applied**
    workaround :you can specify Krut as leaves explicilty 
    let's define 3 domain : 
    
    * root is defaulting to str
    * a is defaulting to list
    * b defaulting to int

 >>> from vector_dict.VectorDict import VectorDict as krut
 >>> from vector_dict.VectorDict import converter as kruter
 >>> a = kruter( { 'a' : Krut( list, {} ),'b' : Krut(int, {}) }, str )  
 >>> a['b']['e'] += 1 
 >>> a['a']['c'] += [ 3 ]
 >>> a['d'] += "toto"
 >>> a.tprint()
 {
     'a' : {
         'c' : [3],
     },
     'b' : {
         'e' : 1,
     },
     'd' : 'toto',
 }

    """
    a_vector_dict = VectorDict()

    for e in iter_object_nl(a_tree, flatten = True):
        a_vector_dict += tree_from_path( 
            *e,
            **dict(defaultdict_factory = defaultdict_factory)
            )
    return a_vector_dict

Element = namedtuple('Element' , "path value")

class Path(tuple):
    def __init__(self, a_tuple):
        """construct a Path from a tuple or a list 
        
 >>> p = Path( [  'a', 'b', 'c' ] )
 >>> p
 >>> ( 'a', 'b', 'c' )
 >>> p = Path( (  'a', 'b', 'c' ) )
 >>> p
 >>> ( 'a', 'b', 'c' )
        """
        self += tuple(a_tuple)

    def endswith( self, *a_tuple ):
        """check if path ends with the consecutive given has argumenbts value
 
 >>> p = Path( [ 'a', 'b', 'c' ] )
 >>> p.endswith( 'b', 'c' )
 >>> True
 >>> p.endswith( 'c', 'b' )
 >>> False
        """
        return self[len(self) - len(a_tuple) : ] == a_tuple

    def startswith( self, *a_tuple ):
        """checks if a path starts with the value 

 >>> p = Path( [ 'a', 'b', 'c', 'd' ] )
 >>> p.startswith( 'a', 'b' )
 >>> True
        """
        return self[: len( a_tuple ) ] == a_tuple

    def _contains( self, a_tuple, _from = 0, follow = 0):
        if len( a_tuple) == follow:
            return True
        index = False
        try:
            here = self[ _from:]
            if len(here ) < len(a_tuple[follow:]):
                return False
        except IndexError:
            return False

        try:
            index = here.index(a_tuple[follow] )
            return  self._contains(
                    a_tuple, 
                        index +  1 , 
                        follow + 1
                    )
        except ValueError:
            return False
        except IndexError:
            return self._contains(a_tuple, _from +  1 )
        return False

    def contains(self, *a_tuple ):
       """checks if the serie of keys is contained in a path
 
 >>> p = Path( [ 'a', 'b', 'c', 'd' ] )
 >>> p.contains( 'b', 'c' )
 >>> True

       """
       return self._contains( a_tuple )

def dot( obj1, obj2):
    """for ease of reading and writing
    equivalent to obj1.dot( obj2 )
    does the leaf by leaf product of the imbricated dict for all 
    the keys that are similar. 

 >>> dot(
        VectorDict( int, dict( x=1 , y=1, z=0) ),
        VectorDict( int, dict( x=1 , y=1, z=1) ),
     ) 
 2.0
    
    """
    return obj1.dot(obj2)

def cos( obj1, obj2):
    """for ease of reading and writing
    equivalent to the cosinus similarity obj1.cos(2)
    returns the cosinus similarity of two vectorDict 
    
 >>> cos(
        VectorDict( int, dict( x=1 , y=1) ),
        VectorDict( int, dict( x=1 , y=0) ),
     ) 
 0.7071067811865475
    """
    return obj1.cos(obj2)



def tree_from_path( *path,**option ):
    """creating a dict from a path

 >>> tree_from_path( 'a', 'b', 'c', 1, defaultdict_factory = int  ).tprint()
 {
     a : {
         b : {
             c : 1,
         },
     },
 }

    """
    default_factory = option.get("default_factory", int)
    path_to_key = list(path)
    root = VectorDict( default_factory, { path_to_key.pop() : path_to_key.pop()})
    current = root
    while len(path_to_key):
        current = VectorDict( default_factory, { path_to_key.pop() : current})
    return current

def can_be_walked(stuff):
    """tells if it is walkable """
    return hasattr(stuff, "__iter__")

def is_generator(stuff):
    """tells if it is a generator"""
    return all( 
        map( 
            lambda prop : hasattr( stuff , prop),
            [ 'next', 'send', 'throw' ]
        )
    )

def flattening(a_duck, taxonomy = can_be_walked ):
    """flattening stuff // adapted from python cookbook"""
    if not taxonomy(a_duck):
        yield a_duck
    else:
        for duckling in a_duck:
            if taxonomy(duckling) and not isinstance( duckling, str) :
                for duck_eggs in flattening(duckling, taxonomy = taxonomy):
                    yield duck_eggs
            else:
                yield duckling



def iter_object_nl(obj, path=(), **opt):
    """
    Generator on all leaves of the object, return an array of the path and the
    leaf

    source:
     http://tech.blog.aknin.name/2011/12/11/walking-python-objects-recursively/
    """

    if isinstance( obj, Mapping ):
        if len(obj):
       
            for key, value in obj.iteritems():
                for child in iter_object_nl(value, path + (key,), **opt):
                    yield  child
        else:
            yield list(path) + [ obj ]
            
    else:
        if opt.get("flatten"):
            yield [ x for x in flattening( path)  ] + [ obj ]
        else:
            yield (path, obj)

def iter_object(obj, path=(), **opt):
    """
    Generator on all leaves of the object, return an array of the path and the
    leaf

    source:
     http://tech.blog.aknin.name/2011/12/11/walking-python-objects-recursively/
    """

    if isinstance(obj, Mapping):
        if len(obj):
            for key, value in obj.iteritems():
                for child in iter_object(value, path + (key,), **opt):
                    yield  child
        else:
            yield (path, obj )

    else:
        yield  opt.get("flatten") and [ 
                x for x in flattening( ( path, obj) ) 
            ] or ( path, obj )

class VectorDict(Adder,Subber,defaultdict):
    """slightly enhanced Dict"""
    def __init__(self, *a , **a_dict ):
        """Constructs like a collections.defaultdict (put sphinx ref)"""
        
        super( VectorDict, self).__init__( *a,**a_dict)

    def from_tree( self, a_tree):
        """Create a VectorDict Intrication from a tree
        Drawback there is no factory specified
        """
        self =  convert_tree( a_tree)

    def match_tree(self, a_tree):
        """does the tree given has an argument match the actual 
        tree.
 if tree leaves are Clauses, the match_tree will apply the clauses.

 **Direct Match**

 >>> a_tree = dict( 
            b = dict( 
                c = 3.0, 
                d = dict( e = True)
            ), 
        )
 >>> complex_dict = convert_tree( a_tree )
 >>> complex_dict.match_tree( dict( c= 3.0 ,d = dict( e = True) ))
 >>> False
 >>> complex_dict.match_tree( dict( b=dict( c=3.0 ,d = dict( e = True) ))
 >>> True

 **Match with clauses**

 >>> from vector_dict.Clause import Clause, anything
 >>> complex_dict.match_tree( dict( b=dict( c=3.0 , d=anything ) ) )
 >>> True
 >>> complex_dict.match_tree({ 'b': { 
    'c': Clause( lambda v : 1 < v < 5), 
    'd' : anything 
 } } )
 >>> True
 
        """

        match_to_find = len(a_tree.keys())
        if not set(a_tree).issubset( set(self.keys())):
            return False
        for k,v in a_tree.iteritems():
            if k in self:
                if is_leaf(v):
                #terminaison of the comparison tree
                    if isinstance(
                            v, Clause
                        ) or isinstance( 
                            v , types.FunctionType
                        ):
                    # if it is a clause apply it to the targeted tree
                        match_to_find -= v(self.get(k)) 
                    else:
                    ## it is not a clause
                        val = self.get(k)
                        ## BUG not all leaves are supposed to support -
                        if  is_leaf(val):
                            match_to_find -=  v == val 
                        else:
                            match_to_find -=  v in val

                else:
                    ## the comparison tree goes on
                    sub_tree = self.get(k)
                    if not is_leaf(sub_tree):
                        ## the compared tree goes on 
                        ## we recurse
                        match_to_find -= sub_tree.match_tree( v )
                    else:
                        ### the compared tree is smaller than the comparison 
                        ## tree
                        match_to_find -= v ==sub_tree
                        #return False
        return 0 == match_to_find


    def build_path( self, *path):
        """ implementation of constructing a path in a tree, argument is 
        a serie of key
 
 >>> a = VectorDict(int, {})
 >>> a.build_path( 'k', 1 )
 >>> a.tprint()
 {
     k = 1,
 }
 >>> a.build_path( 'b', 'n', [ 1 ] )
 >>> a.build_path( 'd', 'e',  2  )
 >>> a.build_path( 'd', 'f',  4  )
 >>> a.tprint()
 {
     k : 1,
     b : {
         n : [1],
     },
     d : {
         e : 2,
         f : 4,
     },
 }

 """
        if len(path) == 2:
            key, value = path[0:2]
            if  key in self.keys() or self.get(key):
                raise ValueError( "collision of values")
            self.__setitem__( key, value )
        if len(path) > 2:
            key, value = path[0:2]
            if key in self.keys() and self.get(key):
                if  value in self[key].keys():
                    self[key].build_path( path[1:])
            else:
                if key in self.keys():
                    raise Exception("Path already present")
            if not is_leaf( self[key] ):
                self[key] +=  tree_from_path( *path[1:] )
            else:
                self.__setitem__(key,  tree_from_path( *path[1:] ))

    def prune(self, *path):
        """delete all items at path 
        
 >>> a  = VectorDict(int, {})
 >>> a.build_path( 'g', 'todel' , True )
 >>> a.build_path( 'g', 'tokeep' , True )
 >>> a.tprint()
 {
     g : {
         tokeep : True,
         todel : True,
     },
 }
 >>> a.prune( 'g', 'todel' )
 >>> a.tprint()
 {
     g : {
         tokeep : True,
     },
 }

"""

        todel = None
        if len(path)>1:
            self.at(path[:-1]).__delitem__(path[-1])
        else:
            self.__delitem__( path[0] )


    def get_at(self, *path):
        """Get a copy of an element at the coordinates given by the path
Throw a KeyError excpetion if the path does not led to an element

 >>> from vector_dict.VectorDict import convert_tree, VectorDict
 >>> intricated = convert_tree( { 'a' : { 'a' : { 'b' : { 'c' :  1 } } } } )
 >>> intricated.get_at( 'a', 'a', 'b' )
 defaultdict(<class 'vector_dict.VectorDict.VectorDict'>, {'c': 1})
 >>> intricated.get_at( 'a', 'a', 'b', 'c' )
 1
 >>> intricated.get_at( 'oops' )
 Traceback (most recent call last):
   File "<input>", line 1, in <module>
   File "vector_dict/VectorDict.py", line 304, in get_at
     return self.at( path, None , True)
   File "vector_dict/VectorDict.py", line 330, in at
     value = here[path[ -1 ] ]
 KeyError: 'oops'
 
 """
        return self.at( path, None , True)

    def at(self, path, apply_here = None, copy = False):
        """
        gets to the mentioned path eventually apply a lambda on the value
        and return the node, 
        and copy it if mentioned. 

 >>> intricated = convert_tree( { 'a' : { 'a' : { 'b' : { 'c' :  1 } } } } )
 >>> pt = intricated.at( ( 'a', 'a', 'b' ) )
 >>> pt
 defaultdict(<class 'vector_dict.VectorDict.VectorDict'>, {'c': 1})
 >>> pt['c'] = 2
 >>> intricated.tprint()
 {
    a : {
        a : {
            b : {
                c : 2,
            },
        },
    },
 }
 >>> intricated.at( ( 'a', 'a', 'b' ), lambda x : x * -2  )
 defaultdict(<class 'vector_dict.VectorDict.VectorDict'>, {'c': -4})
 >>> intricated.pprint()
 a->a->b->c = -4

        """
        here = self
        if apply_here and not( is_function(apply_here) ):
            raise Exception("second argument must be a function to apply on path")
        if not len(path):
            if apply_here:
                raise Exception("cant apply a function on root of %r" % self)
            if copy:
                return  self.copy() 
            return   self
        for e in path[:-1]:
            if not hasattr(here, "__getitem__"):
                raise IndexError("this path dont exists")
            if not here.__getitem__(e):
                raise Exception("Path %r does not exists in the tree" %path ) 
            here = here.__getitem__(e)
        if not apply_here is None:
            here.__setitem__(path[-1],apply_here(here[path[-1]]))
        value = here[path[ -1 ] ]

        if copy and is_container(value):
            return here[path[-1]].copy()
        return value


    def __flatten_generator(func):
        def wrap(*a, **kw):
            return flattening( func( *a, **kw ), taxonomy = is_generator ) 
        wrap.__doc__ = func.__doc__
        return wrap

    #@flatten_generator
    def diff(self, other, diff_mine = None,diff_other=None, path = []):
        """Still In Development. 
        trying to have a tree dif"""

        def prune( key, adict):
            def todo():
                adict.__delitem__(key)
            return [ todo ]

        def cp_if_dict(val):
            return isinstance( v, dict) and v.copy() or v
        if not diff_mine:
            diff_mine = VectorDict( VectorDict, {} )
            diff_other = VectorDict( VectorDict, {} )
        for k, v in self.iteritems():
            if not k  in other.keys():
            ## pour que l'autre me ressemble enlevons toutes les clés
                diff_other += tree_from_path(  * [ path + [k, prune( k, self) ]  ] )
            else:
                ## k in other.keys()
                ## les clés sont dans les deux arbres
                if v != other[k] :
                    if isinstance( v , VectorDict) and isinstance( 
                        other[k], VectorDict):
                        vd_m, vd_o = v.diff(  other[k],  diff_mine, diff_other,  path + [ k ] )
                        diff_mine = diff_mine + vd_m
                        diff_other = diff_other + vd_o
                    elif isinstance( v , VectorDict) or isinstance( 
                        other[k], VectorDict):
                        diff_mine +=  tree_from_path( *[ path + [k, cp_if_dict( other[k]) ] ] )
                    else: 
                        diff_mine +=  tree_from_path( *[  path + [k, - other[k]   ] ] )

                
                else:
                    if isinstance( v, VectorDict ):
                        vd_m, vd_o = v.diff(  other[k],  diff_mine, diff_other,  path + [ k ] )
                        diff_mine = diff_mine + vd_m
                        diff_other = diff_other + vd_o
                    
        for k , v in other.iteritems():
            if not k  in self.keys():
                diff_mine += tree_from_path( *[  path + [k, v ] ] )

        return diff_mine, diff_other
               


   
    @__flatten_generator
    def find(self, predicate_on_path_value, path = tuple() ):
        """apply a fonction on value if predicate on key is found"""
        path = Path( path + tuple() )
        if predicate_on_path_value(Path( path) , self):
            yield  Element( Path( path + tuple() )  ,self )
        for k,v in self.iteritems():
            if isinstance(v, VectorDict ):
                yield  v.find( predicate_on_path_value, Path( path + ( k,)  ) ) 
            else:
                if predicate_on_path_value(Path( path + (k,) ), v):
                    yield  Element( path =  Path( path + (k,))  ,value = v  )

    def  __rdiv__(self, other):
        """reverse division"""
        return self.__div__(other)

    def __idiv__(self, other):
        """immediate division /= """
        return self.__opfactory__(other, False, lambda x,y: x/y , "__internal_divide__" )

    def __div__(self, other):
        """div with copy"""
        return self.__opfactory__(other, True, lambda x,y: x/y , "__internal_divide__" )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        return self.__opfactory__(other, False)

    def __mul__(self, other):
        return self.__opfactory__(other, True)

    def __opfactory__(
            self, 
            other, 
            copy = True, 
            extern_operation = lambda x,y : x*y ,
            intern_operation = "__internal_mul__"
        ):
        """muler"""
        ## __imul__ later
        if not isinstance( self, VectorDict ):
            self, other= other, self
        a_copy = copy and self.copy() or self

        if not isinstance(other, VectorDict):
            for k, v in self.iteritems():
                a_copy[k] = extern_operation( v , other)
            return a_copy
        else:
            return getattr(a_copy, intern_operation)(other)

    def __neg__(self):
        for k, v in self.iteritems():
           self[k] = -1 * v
        return self

    
    def as_vector_iter(self, path=()):
        """
        iterator on key value pair of nested dict in the form of 
        set( key0, key1, key2 ), child
        for a dict, therefore making a n-depth dict being homomorph
        to a single dimension vector in the form of 
        k , v 
        where k is the path, v is the leaf value
        source:
        http://tech.blog.aknin.name/2011/12/11/walking-python-objects-recursively/

 >>> a = convert_tree({ 'a' : { 'a' : { 'r' : "yop" , 'b' : { 'c' :  1 }}}})
 >>> a.tprint()
 {
     a = {
         a = {
             r = 'yop',
             b = {
                 c = 1,
             },
         },
     },
 }
 >>> [ e for e in a.as_vector_iter() ]
 [(('a', 'a', 'r'), 'yop'), (('a', 'a', 'b', 'c'), 1)]
        """
        return iter_object(self,(),flatten=False)
    
    def as_row_iter(self, path=(), **arg): 
        """
        iterator on key value pair of nested dict yielding items in the form
        set( key0, key1, key2 , child)
        very useful for turning a dict in a row for a csv output
        all keys and values are flattened

 >>> a = convert_tree({ 'a' : { 'a' : { 'r' : "yop" , 'b' : { 'c' :  1 }}}})
 >>> a.tprint()
 {
     a : {
         a : {
             r : 'yop',
             b : {
                 c : 1,
             },
         },
     },
 }
 >>> [ e for e in a.as_row_iter() ]
 [['a', 'a', 'r', 'yop'], ['a', 'a', 'b', 'c', 1]]


        """
        arg["flatten"] = arg.get("flatten", True)
        return iter_object(self,(),**arg )

    def __not__(self):
        """ not on all leaves of the dict

 >>> from vector_dict.VectorDict import convert_tree, VectorDict,Element,Path
 >>> a = convert_tree(dict(a = dict(tt=True, tf=True, ft=False, ff=False), c= False))
 >>> a.__not__().tprint()
 {
     a : {
         tf : False,
         tt : False,
         ft : True,
         ff : True,
     },
     c : True,
 }
 >>> a.tprint()
 {
     a : {
         tf : True,
         tt : True,
         ft : False,
         ff : False,
     },
     c : False,
 }

"""

        new_dict=self.copy()
        for k, v in new_dict.iteritems():
            if not isinstance(v, VectorDict):
                new_dict[k] = not v
            else:
                new_dict[k] = v.__not__()
        return new_dict


    def __or__(self,other):
        """or on all leaves

 >>> b = convert_tree(dict(a = dict(tt=True, tf=False, ft=True, ff=False), b= True))
 >>> a = convert_tree(dict(a = dict(tt=True, tf=True, ft=False, ff=False), c= False))
 >>> ( b | a).tprint()
 {
     a : {
         tf : True,
         tt : True,
         ft : True,
         ff : False,
     },
     c : False,
     b : True,
 }
"""

        new_dict = self.copy()
        common_key = set( self.keys() ) & set(other.keys() )
        for k in common_key:
                new_dict[k] = (self[k]).__or__( other[k] )
        for k in set( other.keys()) - common_key:
            new_dict[k] =  other[k] 
            
        return new_dict

    def __and__(self,other):
        """and on all leaves

 >>> b = convert_tree(dict(a = dict(tt=True, tf=False, ft=True, ff=False), b= True))
 >>> a = convert_tree(dict(a = dict(tt=True, tf=True, ft=False, ff=False), c= False))
 >>> ( b & a).tprint()
 {
     a : {
         tf : False,
         tt : True,
         ft : False,
         ff : False,
     },
 }
"""

        common_key =  set( self.keys() ) &  set( other.keys() )
        new_dict = VectorDict(VectorDict, dict() )
        for k in common_key:
                new_dict[k] = (self[k]).__and__( other[k] )
        return new_dict

    def __xor__(self,other):
        """xor on all leaves 
 >>> b = convert_tree(dict(a = dict(tt=True, tf=False, ft=True, ff=False), b= True))
 >>> a = convert_tree(dict(a = dict(tt=True, tf=True, ft=False, ff=False), c= False))
 >>> ( b ^ a).tprint()
 {
     'a' : {
         'tf' : False,
         'tt' : True,
         'ft' : False,
         'ff' : True,
     },
 }
"""


        return (  self.__not__() & other ) | ( other.__not__() & self )

    def intersection(self, other, ignore_value_difference=False):
        """Return all elements common in two different trees
        raise an exception if both leaves are different

        #TOFIX : dont make a newdict if doing in place operations


 >>> from vector_dict.VectorDict import convert_tree, VectorDict,Element,Path
 >>> a = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 2  ) ) } )
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, d = 1  ) ) } )
 >>> a.intersection(b).tprint()
 {
     a : {
         b : 1,
     },
 }
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 1  ) ) } )
 >>> a.intersection(b).tprint()
 Traceback (most recent call last):
   File "<input>", line 1, in <module>
   File "vector_dict/VectorDict.py", line 634, in intersection
     new_dict[k] = (self[k]).intersection( other[k] )
   File "vector_dict/VectorDict.py", line 639, in intersection
     other[k]
 Exception: ('CollisionError', '2 != 1')
 >>> a.intersection(b, ignore_value_difference=True).tprint()
 {
   'a' : {
      'c' : 2,
      'b' : 1,
   },
 }

"""

        common_key =  set( self.keys() ) &  set( other.keys() )
        new_dict = VectorDict(VectorDict, dict() )
        for k in common_key:
        ## and what about sets ? 
        ## try a key or value made of a forzen set
            if  hasattr( self[k], "intersection") :
                new_dict[k] = (self[k]).intersection( other[k], ignore_value_difference )
            else:
            	if not ignore_value_difference:
                    if self[k] != other[k]:
                        raise Exception("CollisionError","%s != %s" % (  
                                self[k] ,
                                other[k]
                            ) )
                new_dict[k] = self[k]
        return new_dict or VectorDict()
    
    def union(self, other, intersection=None):
        """return the union of two dicts

 >>> from vector_dict.VectorDict import convert_tree, VectorDict,Element,Path
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 1  ) ) } )
 >>> a = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, d = 2, c=1  ) ), 'e' :  1 } )
 >>> b.union(a)
 defaultdict(<type 'int'>, {'a': defaultdict(<type 'int'>, {'c': 1, 'b': 1, 'd': 2}), 'e': 1})
 >>> a = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, d = 2, c=3  ) ) } )
 >>> b.union(a)
 Traceback (most recent call last):
   File "<input>", line 1, in <module>
   File "vector_dict/VectorDict.py", line 669, in union
     return self + other - self.intersection(other)
   File "vector_dict/VectorDict.py", line 658, in intersection
     new_dict[k] = (self[k]).intersection( other[k] )
   File "vector_dict/VectorDict.py", line 663, in intersection
     other[k]
 Exception: ('CollisionError', '1 != 3')
 

"""
    ###Dont work
        #return - self.intersection(other) + self + other
        ## take  intersection 
        union  = intersection or self.intersection(other)
        ## add self not in intersection
        ### easy case

        common_keys = set( union.keys() ) 
        orthogonal_keys_self = set(self).symmetric_difference( set( union.keys() ))
        orthogonal_keys_other = set(other).symmetric_difference( set( union.keys() ) )


        for k in orthogonal_keys_self:
            if not is_leaf(self[k]):
                union[k] += self[k]
            else:
               raise( Exception("Wtf?") )
        
        for k in orthogonal_keys_other:
            if not is_leaf(other[k]):
                union[k] += other[k]

        for k in common_keys:
            if not self[k] == other[k]:
                if isinstance(union[k], VectorDict) :
                    union[k] = self[k].union(other[k], intersection and intersection.get(k) or VectorDict()  )
                else: 
                    union[k] = self[k].union(other[k])
        return union
    
    def symmetric_difference( self, other):
        """ return elements present only elements in one of the dict
        Throw a Collision Error if two leaves in each tree are different

 >>> from vector_dict.VectorDict import convert_tree, VectorDict,Element,Path
 >>> a = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, d = 2, c=1  ) ), 'e' :  1 } )
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 1   ) ) } )
 >>> a.symmetric_difference(b)
 defaultdict(<type 'int'>, {'a': defaultdict(<type 'int'>, {'d': 2}), 'e': 1})
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 2   ) ) } )
 >>> a.symmetric_difference(b)
 Traceback (most recent call last):
   File "<input>", line 1, in <module>
   File "vector_dict/VectorDict.py", line 694, in symmetric_difference
     for path,v in self.intersection(other).as_vector_iter():
   File "vector_dict/VectorDict.py", line 658, in intersection
     new_dict[k] = (self[k]).intersection( other[k] )
   File "vector_dict/VectorDict.py", line 663, in intersection
     other[k]
 Exception: ('CollisionError', '1 != 2')


"""
        new_dict = self + other
        for path,v in self.intersection(other).as_vector_iter():
            new_dict.prune( *path )
        return new_dict

    def issubset( self, other ):
        """tells if all element of self are included in other

 >>> from vector_dict.VectorDict import convert_tree, VectorDict,Element,Path
 >>> a = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, d = 2, c=1  ) ), 'e' :  1 } )
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 1   ) ) } )
 >>> b.issubset(a)
 True
 >>> a.issubset(b)
 False

"""
        return self.intersection(other) == self

    def issuperset(self, other):
        """tells if all element of other is included in self
throws an exception if two leaves in the two trees have different 
values

 >>> from vector_dict.VectorDict import convert_tree, VectorDict,Element,Path
 >>> a = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, d = 2, c=1  ) ), 'e' :  1 } )
 >>> b = VectorDict( int, { 'a' : VectorDict( int, dict( b = 1, c = 1   ) ) } )
 >>> a.issuperset(b)
 True
 >>> b.issuperset(a)
 False

"""

        return self.union(other) == self

    def __internal_divide__(self, other):
        """dividing two vectors internaly"""

        common_key =  set( self.keys() ) &  set( other.keys() )
        ## how could I get the factory of the default dict ? 
        new_dict = VectorDict(VectorDict, dict() )
        for k in common_key:
            if  hasattr( self[k], "__internal_divide__") :
                new_dict[k] = (self[k]).__internal_divide__( other[k] )
            else:
                new_dict[k] = self[k] / other[k]
        return new_dict

    def __internal_union__(self, other, copy = True):
        """what to do when you do an union on two dicts ? """
        common_key =  set( self.keys() ) &  set( other.keys() )
        new_dict = copy and VectorDict( None, {} ) or self
        for k in common_key:
            if  hasattr( other[k], "__internal_union__") :
                new_dict[k] = (self[k]).__internal_union__( other[k] )
            else:
                new_dict[k] = self[k] * other[k]

    def __internal_mul__(self, other):
        """multiplying to vectors as one vector of homothetia * vector
        it is a shortcut for a multiplication of a diagonal matrix
        missing keys in the pseudo diagonal matrix are pruned"""
        
        common_key =  set( self.keys() ) &  set( other.keys() )
        ## how could I get the factory of the default dict ? 
        ## hum hum, and what about in place modification ? 
        new_dict = VectorDict(VectorDict, dict() )
        for k in common_key:
            if  hasattr( self[k], "__internal_mul__") :
                new_dict[k] = (self[k]).__internal_mul__( other[k] )
            else:
                new_dict[k] = self[k] * other[k]
        return new_dict
    
    def dot(self, other):
        """scalar  = sum items self * other for each distinct key in common
        norm of the projection of self on other"""
        return sum( [ 1.0 * v for k,v in ( self * other ).as_vector_iter()  ] )
    
    #def values(self):
    #    return ( v for k,v in self.as_vector_iter() )

    def norm(self):
        """norm of a vector dict = sqrt( a . a  )"""
        return sqrt(self.dot(self))

    def cos( self, other ):
        """cosine similarity of two vector dicts
        a . b / ( ||a||*||b|| )
        """
        return 1.0 * self.dot( other) / self.norm() / other.norm()

    def jaccard(self, other):
        """jaccard similariry of two vectors dicts
        a . b  / ( ||a||^2 + ||b||^2 - a . b )
        """
        return 1.0 * self.dot(other) / (
            float( self.norm()) ** 2 +
            float( other.norm()) ** 2-
            self.dot(other) 
        )



    def tformat(self, indent_level = 0, base_indent = 4):
        """pretty printing in a tree like form a la Perl"""
        offset = " " *  indent_level * base_indent
        toreturn = '{\n'
        for k,v in self.iteritems():
            toreturn += offset + ( " " * base_indent ) +  '%s : ' %( 
                repr(k) or '<BUG>')
            if hasattr( v, "tformat"):
                toreturn += v.tformat( indent_level+1, base_indent )
            else:
                toreturn += "%s" % ( isinstance( v, ( str, unicode) ) and ( "'%s'" % v ) or repr(v) )
            toreturn += ',\n'
        toreturn += offset +  '}'
        return toreturn

    def tprint( self, indent_level = 0, base_indent = 4):
        """pretty printing with indentation in tradiotionnal fashion"""
        print self.tformat( indent_level, base_indent )

    def pformat(self):
        return  "\n".join( [
                    "%s = %s" % (
                        "->".join( map(unicode, x[0])), 
                       isinstance( x[1], ( str, unicode) ) and ( "'%s'" % x[1] ) or repr(x[1])  
                    ) for x in self.as_vector_iter() ] )
    def pprint(self):
        """ pretty printing the VectorDict in flattened vectorish representation"""
        print self.pformat()
