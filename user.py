class facebookUser:
    #Store all the user info here for quick access

    def __init__(self):
        self.senderID = None
        self.name = None

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getID(self):
        return self.senderID

    def setID(self, id):
        self.senderID = id
