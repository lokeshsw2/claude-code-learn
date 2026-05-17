def greet(**kw):
    print(f"Name: {kw['name']}, Age: {kw['age']}")


if __name__ == '__main__':
    d  = {'name': 'alice', 'age': 20}
    greet(**d)