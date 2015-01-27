import kengen.parsers.xml_format1
import kengen.codegen.pyxon

def main(model_file, target_dir):
    parser = kengen.parsers.xml_format1
    writer = kengen.codegen.pyxon

    writer.generate_source(parser.load_model(model_file),
                           target_dir)


if __name__=='__main__':
    print "oooooooh yeah here we go!"
    import sys
    args = sys.argv[1:]
    main(*args)
        
