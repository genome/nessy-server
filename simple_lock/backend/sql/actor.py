class Actor(object):
    def __init__(self, session):
        self.session = session

    def close(self):
        self.session.close()
