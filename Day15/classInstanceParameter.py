class Person:
    name = "Person"
    def __init__(self, name = None):
        self.name = name

jon = Person("Jon")
print("%s name is %s" % (Person.name, jon.name))
anderson = Person()
anderson.name = "Anderson"
print("%s name is %s" % (Person.name, anderson.name))
