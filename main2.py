def name_generator(name):

    name = name.split(' ')

    first = name[0].replace(name[0][0:2], name[1][0:2])
    last = name[1].replace(name[1][0:2], name[0][0:2])

    print(first + " " + last)


name_generator('Sam Lambert')
name_generator('Dixon Cox')
