from states import BaseState
class StateMachine:
    def __init__(self, states,screen):
        self.states:dict = states
        self.current_state:"BaseState" = None
        self.screen = screen
        self.current_state_key = None
    def change(self,key, initial_params={}):
        if not key in self.states.keys():
            raise KeyError("State not Found")
        if self.current_state:
            self.current_state.exit()
        self.current_state_key = key
        new_state  = self.states[key](state_machine = self,screen = self.screen,**initial_params)
        self.current_state = new_state
        self.current_state.enter()
    def key_event(self,key):
        self.current_state.key_event(key)
    def key_up_event(self,key):
        self.current_state.key_up_event(key)

    def render(self):
        if not self.current_state:
            raise Exception("Current state not set")
        self.current_state.render()
    def logic(self):
        if not self.current_state:
            raise Exception("Current state not set")
        self.current_state.logic()   

        