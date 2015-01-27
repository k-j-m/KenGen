import os
import shutil

def generate_source(classes, target_dir, module_path=('default',)):
    assert os.path.isdir(target_dir), "Make sure that directory exists: %s" % target_dir

    src_dir = os.path.join(target_dir, *module_path)
    # recursively make directories
    if os.path.exists(src_dir):
        shutil.rmtree(src_dir)
    os.makedirs(src_dir)

    for cls in classes:
        generate_class(cls, src_dir)

def generate_class(cls, src_dir):
    lines = []

    # start with imports
    lines.append('import something.something.something')

    # some whitespace
    lines.append('\n')
    
    lines.append('public class %s {' % cls.name)

    for attr,type_ref in cls.attrs.iteritems():
        lines.append('    public final %s %s;' % (attr,type_ref_to_java(type_ref)))

    src_file = os.path.join(src_dir, cls.name + '.java')
    open(src_file,'w').write('\n'.join(lines))

def type_ref_to_java(type_ref):
    return type_ref.type_
