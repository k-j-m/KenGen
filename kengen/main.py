import kengen.parsers.xml_format1
import kengen.codegen.jackson
import kengen.codegen.pyxon
import os

generators = [['pyxon',kengen.codegen.pyxon],
              ['jackson',kengen.codegen.jackson]]

def main(model_file, target_dir):
    assert os.path.exists(target_dir)
    
    parser = kengen.parsers.xml_format1
    for name, writer in generators:

        #writer = kengen.codegen.jackson
        #writer = kengen.codegen.pyxon
        source_dir = os.path.join(target_dir, name)
        if not os.path.exists(source_dir):
            os.mkdir(source_dir)
            
        writer.generate_source(parser.load_model(model_file),
                               source_dir)


if __name__=='__main__':
    print "oooooooh yeah here we go!"
    import sys
    args = sys.argv[1:]
    main(*args)
        
