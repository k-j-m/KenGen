
# This is NASTY! This is meant to be language neutral in here
# I guess I need to add some language specific (but not library
# specific) utility modules.

# A list of what builtin data types we support.
python_primitives = ['float','int','string','boolean']
python_structures = ['List', 'Map']

class ClassElement(object):
    """
    ClassElement class contains a description of a class in our data
    model.

    Please note that I've made sure to keep this class completely unaware
    of the format of the model. Please don't let the xml (or replacement format)
    slip in here.

    Note:
    We don't currently support user classes with generics/type-parameters.
    """
    def __init__(self, name, attrs, extends, class_parameters, isabstract):
        """
        All values are set in the constructor and must be read by the parser.
        """
        self.name = name
        self.attrs = attrs
        self.extends = extends
        self.class_parameters = class_parameters
        self.isabstract = isabstract

    def get_precedents(self):
        """
        Returns a list of all types that are referenced by this class.
        This is especially important when generating the python code
        since the python classes need to be written in an order such that
        all classes are read by the interpreter before they are referenced.
        """
        precedents=[]

        if not self.extends is None:
            precedents.append(self.extends)
        
        for type_ref in self.attrs.values():
            precedents.extend(type_ref.get_precedents())
        return precedents
        
class TypeRef(object):
    """
    This class is the nuts-and-bolts of our type-system.
    It contains the type name and a {name:type_ref} dict
    of all nested type parameters. An example of this is a
    list where all of the items must be of a certain type.

    In Java-speak: List<Integer> or Map<String,Double>
    """
    def __init__(self, type_, type_params={}):
        """
        Value constructor.
        All of the info needs to be parsed from the data model by code
        in another module. That is not the job here!
        """
        self.type_ = type_
        self.type_params = type_params

    def get_precedents(self):
        """
        Returns a list of all types that need to be available
        to be able to use this type (including the top level
        type itself and the types of any nested attributes).
        """
        precedents = [self.type_]
        for tp in self.type_params.values():
            precedents.extend(tp.get_precedents())

        return precedents
        
    def __repr__(self):
        return 'TypeRef(%s, %s)'%(self.type_, repr(self.type_params))


def order_classes(classes):
    """
    Function orders classes such that they can be written with
    no classes being referenced before they are read by the interpreter.

    Note that this will raise an error in the following 2 cases:
    + Circular dependencies
    + Mistakenly underfined types 
    """
    unsorted_classes = classes[:]
    sorted_classes = []
    custom_types=[]
    for _ in range(len(classes)):
        nxt_class,unsorted_classes = find_resolved_class(unsorted_classes,custom_types)
        sorted_classes.append(nxt_class)
        custom_types.append(nxt_class.name)

    return sorted_classes
        
def find_resolved_class(classes, custom_types):
    """
    Takes a list of classes and a list of already-defined custom_types
    and returns a class with no unresolved dependencies and a list
    of the remaining classes.
    """
    assert len(classes) > 0, 'Trying to find a class in an empty list...'
    
    ok_classes = [c for c in classes
                  if class_is_resolved(c, custom_types)]

    if len(ok_classes) == 0:
        raise Exception("Can't find any resolved classes. Check for circular dependencies or undefined types.")

    classes2=classes[:]
    classes2.remove(ok_classes[0])
    return ok_classes[0],classes2
                
def class_is_resolved(cls_elem, custom_types):
    """
    Returns true of the given class element doesn't require
    any data types that are not in the builtins or the list
    of custom_types passed in as the 2nd argument.
    """
    precedents = cls_elem.get_precedents()

    def check_type(type_name):
        return type_is_resolved(type_name, custom_types)
    
    return all(map(check_type, precedents))
    
def type_is_resolved(type_name, custom_types):
    """
    Returns true of the given type_name is found either in
    the builtins or the list of custom_types passed in
    as the 2nd argument.
    """
    return any([type_name in python_primitives,
                type_name in python_structures,
                type_name in custom_types])
