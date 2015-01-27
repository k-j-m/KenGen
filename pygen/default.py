
from pyxon.decode import subtyped, extending, sprop, cprop
from pyxon.utils import transform_list, transform_map, identity, objectify, unobjectify, obj

@subtyped(using='@type')
class AbstractClass(object): pass

@sprop.name #string
@extending(AbstractClass, named='SomeClass2')
class SomeClass2(AbstractClass): pass

@sprop.age #int
@sprop.name #string
@extending(AbstractClass, named='SomeClass3')
class SomeClass3(AbstractClass): pass

@cprop.y(obj(AbstractClass), unobjectify)
@sprop.x #int
@cprop.z(transform_list(obj(AbstractClass)), transform_list(unobjectify))
@cprop.a(transform_map(identity, identity), transform_map(identity, identity))
class TopClass(object): pass