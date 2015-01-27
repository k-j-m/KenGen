import xml.etree.ElementTree as ET

from kengen.model import ClassElement, TypeRef

def load_model(model_file):
    tree = ET.parse(model_file)
    model = tree.getroot()
    classes = parse_model(model)
    return classes

def str_to_bool(boolstring):
    """
    Helper to get the boolean value of a string.
    """
    truths = ['true', 't', 'yes', 'y', 'ok']
    return boolstring.lower() in truths

def parse_model(elem):
    """
    Takes a Model ElementTree element and returns
    a list of ClassElement objects created from the xml data.
    """
    assert elem.tag == 'Model'
    classes = [parse_class(c) for c in elem]
    return classes

def parse_class(elem):
    """
    Takes a Class ElementTree element and returns a
    ClassElement object that is created from the xml data.
    """
    assert elem.tag == 'Class'

    name = elem.attrib['name']
    str_isabstract = elem.attrib.get('isabstract','false')

    isabstract = str_to_bool(str_isabstract)
    
    extends = elem.attrib.get('extends') # default = None
    params = dict([(k,v) for k,v in elem.attrib.iteritems()
                   if not k in ['name','extends']])

    attrs = dict([parse_class_attribute(a) for a in elem])
    
    return ClassElement(name, attrs, extends, params, isabstract)          


def parse_class_attribute(elem):
    """
    Takes a class's Attribute xml element and returns
    a name,value tuple containing the attribute's name
    and a typeref for the value.

    This is an awkward description: do better.
    """
    
    assert elem.tag == "Attribute"
    assert len(elem)==1
    
    name = elem.attrib['name']
    typeref = parse_typeref(elem[0])

    return name,typeref

def parse_typeref(elem):
    """
    Pass in a typeref xml element and return a typeref class
    including any nested type parameters.
    """
    assert elem.tag == "TypeRef"
    type_ = elem.attrib['type']

    # Recurse on nested elements, which contain extra type parameters
    # Q: does this work for type parameters for user defined classes
    # as well? I think it ought to, but how do we turn that into code?
    # Also, how to we handle the parameter ordering?
    # MyClass<p1,p2>: MyClass<String,Int> <==> MyClass<Int,String>
    params = dict([(e.tag,parse_typeref(e[0])) for e in elem])
    return TypeRef(type_, params)

