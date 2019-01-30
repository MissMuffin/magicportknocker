from state import State
import state
import os

def test_save_and_load():
    state.file_name = "test.json"
    s = State("secret", 9)
    s.save()

    read_state = State.load()

    assert s.secret == read_state.secret 
    assert s.number_of_remaining_tickets == read_state.number_of_remaining_tickets

    os.remove(state.file_name)

