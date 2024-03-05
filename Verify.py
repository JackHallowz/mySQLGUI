def scanthrough(user, password):
    if len(user) == 0 or len(password) == 0:
        print("Can't be empty")
        raise Exception("This is an error")