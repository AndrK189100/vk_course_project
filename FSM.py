class FSM:
    def __init__(self, state: object):
        self.active_state = state
        pass

    def set_state(self, state: object):
        self.active_state = state
        pass

    def update(self, event: object):
        self.active_state(event)
