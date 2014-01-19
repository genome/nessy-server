class Actor(object):
    def __init__(self, session):
        self.session = session

    def cleanup(self):
        self.session.close()
