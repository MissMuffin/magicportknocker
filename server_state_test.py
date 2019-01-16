import server_state
from server_state import *
import pytest
import uuid

@pytest.fixture
def state():
    filename = str(uuid.uuid4()) + ".json"
    state = ServerState(save_file=filename)
    state.remove_all_users()
    yield state
    os.remove(filename)

def test_create_and_save(state):
    state.save()
    print(state._save_file)
    loaded = ServerState(save_file=state._save_file)
    loaded.load()
    assert loaded.id_count == 0 and isinstance(loaded.users, list)
    assert state.id_count == loaded.id_count and state.users == loaded.users

def test_add_one(state):
    state.add_user("tim", 10, [1, 2, 3])
    assert state.users[0].user_name == "tim"
    assert state.id_count == 1

def test_add_one_and_load(state):
    state.add_user("tim", 10, [1, 2, 3])
    loaded = ServerState(save_file=state._save_file)
    loaded.load()
    assert len(loaded.users) == len(state.users)
    assert loaded.id_count == state.id_count
    assert loaded.users[0].user_name == "tim"

def test_remove_user(state):
    state.add_user("karl", 5, [6,7])
    state.add_user("zoe", 5, [6,7])
    for user in state.users:
        if user.user_name == "karl":
            user_id_to_be_removed = user.user_id
    removed = state.remove_user_by_id(user_id_to_be_removed)
    assert len(state.users) == 1
    assert removed.user_name == "karl"

    loaded = ServerState(save_file=state._save_file)
    loaded.load()
    assert len(loaded.users) == len(state.users)
    assert loaded.id_count == state.id_count

def test_get_user(state):
    state.add_user("karl", 5, [6,7])
    state.add_user("zoe", 5, [6,7])
    gotten = state.get_user(1)
    assert len(state.users) == 2
    assert gotten != None
    assert gotten.user_name == "zoe"
