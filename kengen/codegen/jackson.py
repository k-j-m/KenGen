import os
import shutil

type_template = '@Type(name={0}, value={0}.class)'
jsonsubtype_tmpl = '@JsonSubTypes({{{0}}})' # literal {braces} need doubled up
jsontypeinfo = '@JsonTypeInfo(use=JsonTypeInfo.Id.NAME, include=JsonTypeInfo.As.PROPERTY, property="@type")'

def generate_source(model, target_dir):
    classes = model.classes
    module_path = model.package.split('.')
    assert os.path.isdir(target_dir), "Make sure that directory exists: %s" % target_dir

    src_dir = os.path.join(target_dir, *module_path)
    # recursively make directories
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
    os.makedirs(src_dir)

    for cls in classes:
        generate_class(cls, classes, module_path, src_dir)

def generate_class(cls, classes, module_path, src_dir):
    lines = []

    imports = []

    # get class annotations
    class_annotations = get_class_annotations(cls, classes, imports)

    # get attribute info
    attributes = [get_attribute(nm,type_ref) for nm,type_ref in cls.attrs.iteritems()]
        
    # get package declaration
    package = get_package(module_path)

    # get class declaration
    class_declaration = get_class_declaration(cls)
    
    # now we can just do the rest by hand
    lines.append(package)
    lines.append('')
    lines.extend(imports)
    lines.append('')
    lines.extend(class_annotations)
    lines.append(class_declaration)
    
    # attr lines
    attr_lines = [get_attribute(nm, type_ref)
                  for nm,type_ref in cls.attrs.iteritems()]

    lines.extend(attr_lines)
    lines.append('}')
    
    src_file = os.path.join(src_dir, cls.name + '.java')
    open(src_file,'w').write('\n'.join(lines))

def get_package(module_path):
    return 'package ' + '.'.join(module_path) + ';'
    
def get_imports(cls):
    return []

def get_class_annotations(cls,classes,imports):
    annots = []
    if cls.isabstract:
        imports.append('com.fasterxml.jackson.annotation.JsonSubTypes;')
        imports.append('com.fasterxml.jackson.annotation.JsonSubTypes.Type;')
        imports.append('com.fasterxml.jackson.annotation.JsonTypeInfo;')
        
        annots.append(jsontypeinfo)

        subclasses = [c for c in classes if c.extends == cls.name]
        subtype_annots = [type_template.format(c.name)
                          for c in subclasses]

        
        jsonsubtype = jsonsubtype_tmpl.format(','.join(subtype_annots))
        annots.append(jsonsubtype)

    return annots

def get_attribute(nm, type_ref):
    return '    public final {0} {1};'.format(nm, type_ref_to_str(type_ref)) 

def type_ref_to_str(type_ref):
    t = javaise_typename(type_ref.type_)

    # A little mind-bendy
    # Each type parameter has a name (eg key, value, ...) and an
    # associate type_ref, which we want to represent as a string
    # Perfectly suited to a recursive call.
    type_params = [type_ref_to_str(tp[1])
                   for tp in type_ref.type_params]

    if len(type_params)>0:
        return t + '<%s>'% ','.join(type_params)
    else:
        return t

def get_class_declaration(cls):
    if cls.isabstract:
        abstract_token = ' abstract'
    else:
        abstract_token = ''

    if cls.extends is not None:
        extends_token = ' extends {0}'.format(cls.extends)
    else:
        extends_token = ''
        
    return 'public {0} class {1} {2} {{'.format(abstract_token, cls.name, extends_token)

def javaise_typename(type_name):
    type_map = { 'string':'String' }
    return type_map.get(type_name, type_name)
