"""
Module creates code for use with the Paxon JSON-to-Python library.

Coincidentally I am also the author of that library. Go figure.
"""
import os

from kengen.model import order_classes
from kengen.model import python_primitives, python_structures

def generate_source(classes, target_dir, module_path=('default',)):
    assert os.path.isdir(target_dir), "Make sure that directory exists: %s" % target_dir

    fname = module_path[-1] + '.py'
    sub_dirs = module_path[:-1]
    target_dir2 = os.path.join(target_dir, *sub_dirs)
    
    if not os.path.exists(target_dir2):
        os.makedirs(target_dir2)

    with open(os.path.join(target_dir2,fname),'w') as src_file:
        src_string = get_source_string(classes)
        src_file.write(src_string)

def get_source_string(classes):
    imports = """
from pyxon.decode import subtyped, extending, sprop, cprop
from pyxon.utils import transform_list, transform_map, identity, objectify, unobjectify, obj\n\n"""
    return imports + classes_to_python(classes)



def class_to_python(class_element):
    """
    Takes a class_element and converts it into a source-code string.
    """
    lines = []
    attrs = class_element.attrs

    for attr_nm, type_ref in attrs.iteritems():
        lines.append(class_annotation(attr_nm, type_ref))

    extends = class_element.extends
    name = class_element.name
    
    if not extends is None:
        lines.append('@extending(%s, named=\'%s\')' % (extends, name))

    if class_element.isabstract:
        lines.append('@subtyped(using=\'@type\')')
        
    if extends is None:
        superclass = 'object'
    else:
        superclass = extends

    lines.append('class %s(%s): pass' % (name, superclass))
    return '\n'.join(lines)


def class_annotation(nm, type_ref):
    """
    Returns the class property annotation for the given
    name and type_ref.

    This function dispatches the call based on whether the
    type_ref is a builtin primitive or if it is a complex
    datatype (either list, map or custom class).
    """
    if type_ref.type_ in python_primitives:
        return simple_attr_annotation(nm, type_ref)
    else:
        return complex_attr_annotation(nm,type_ref) 

def simple_attr_annotation(nm, type_ref):
    """
    Returns a simple class property annotation for the
    given name and type_ref.
    """
    assert type_ref.type_ in python_primitives
    return '@sprop.%s #%s' % (nm, type_ref.type_)

def complex_attr_annotation(nm, type_ref):
    """
    Returns a complex class property annotation for the given
    name and type ref.
    """
    marshalfun, unmarshalfun = type_ref_marshal_funs(type_ref)
    return '@cprop.%s(%s, %s)' % (nm, marshalfun, unmarshalfun)


def type_ref_marshal_funs(type_ref):
    """
    Entry point for a recursive polymorphic function.
    The function call gets dispatched accordingly
    depending on the type of the type reference
    passed in as an argument.
    Primitives, Maps, Lists and other objects are
    all treated seperately.
    Type parameters for user defined classes are not
    currently possible. I need to figure out the
    code syntax for them first of all.

    Returns:
    (marshal-function, unmarshal-function)

    Where each item in the tuple is a string containing
    the source code needed to convert between json->python
    and python->json
    """

    # fairly nasty case style dispatch
    type_ = type_ref.type_
    if type_ in python_primitives:
        return primitive_marshal_funs(type_ref)
    elif type_ == 'Map':
        return map_marshal_funs(type_ref)
    elif type_ == 'List':
        return list_marshal_funs(type_ref)
    else:
        return object_marshal_funs(type_ref)
    
def primitive_marshal_funs(type_ref):
    """
    Marshal functions for a python primitive.
    This is the base case for our recursive function.
    """
    assert type_ref.type_ in python_primitives
    return ('identity', 'identity')

def map_marshal_funs(type_ref):
    """
    Returns the marshal functions for a map type_ref.
    These may contain many layers of nested function calls,
    as in the following example:
    Map<String,Map<String,Map<String,SomeThing>>>
    """
    assert type_ref.type_ == 'Map'

    key_type_ref = type_ref.type_params['Key']
    #key_marshal, key_unmarshal = type_ref_marshal_funs(key_type_ref)
    # SPECIAL TREATMENTFOR KEYS
    assert key_type_ref.type_ == 'string'
    key_marshal = 'identity'
    key_unmarshal = 'identity'
    
    val_type_ref = type_ref.type_params['Value']
    val_marshal, val_unmarshal = type_ref_marshal_funs(val_type_ref)

    template = 'transform_map(%s, %s)'

    marshal_fun = template % (key_marshal, val_marshal)
    unmarshal_fun = template % (key_unmarshal, val_unmarshal)
    
    return marshal_fun, unmarshal_fun

def list_marshal_funs(type_ref):
    """
    Returns the marshal functions for a list data type.
    """
    assert type_ref.type_ == 'List'

    item_type_ref = type_ref.type_params['Item']
    item_marshal, item_unmarshal = type_ref_marshal_funs(item_type_ref)

    template = 'transform_list(%s)'
    marshal_fun = template % item_marshal
    unmarshal_fun = template % item_unmarshal

    return marshal_fun, unmarshal_fun

def object_marshal_funs(type_ref):
    """
    Returns the marshal functions for a custom class.

    NOTE: THIS DOESN'T SUPPORT TYPE PARAMETERS
    I need to first figure out whether there is a use case
    and then work out how to handle it.
    """    
    # WHAT TO DO WITH THESE? NEED TO FIGURE OUT
    # THE SYNTAX IN THE CODE!
    type_params = type_ref.type_params
    
    marshal_fun = 'obj(%s)' % type_ref.type_
    unmarshal_fun = 'unobjectify'
    return marshal_fun, unmarshal_fun

def classes_to_python(class_elements):
    """
    This is not so simple as just producing the code for each class
    because we need to be super careful to write the classes in the
    right order because of hte way that the python interpreter loads
    classes as it sees them.

    Example - this is BAD:

    class ConcreteClass(AbstractClass): pass
    class AbstractClass(object): pass

    The ConcreteClass references the AbstractClass before it has been
    loaded by the interpreter.

    Instead we need to figure out any dependencies and make sure that
    the classes are written in the right order.

    class AbstractClass(object): pass
    class ConcreteClass(AbstractClass): pass

    This is handled by re-ordering the order that hte classes are written
    using the order_classes(class_elements) function.
    """
    ordered_classes = order_classes(class_elements)
    return '\n\n'.join(map(class_to_python, ordered_classes))


