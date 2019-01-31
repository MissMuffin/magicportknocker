from .server_state import *
import pytest
import uuid
import base64


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
    tim = state.get_user(0)
    loaded = ServerState(save_file=state._save_file)
    loaded.load()
    loaded_tim = loaded.get_user(0)
    assert len(loaded.users) == len(state.users)
    assert loaded.id_count == state.id_count
    assert loaded_tim.user_name == tim.user_name
    assert loaded_tim.symm_key == tim.symm_key


def test_remove_user(state):
    state.add_user("karl", 5, [6, 7])
    state.add_user("zoe", 5, [6, 7])
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
    state.add_user("karl", 5, [6, 7])
    state.add_user("zoe", 5, [6, 7])
    gotten = state.get_user(1)
    assert len(state.users) == 2
    assert gotten != None
    assert gotten.user_name == "zoe"


def test_generate_client_setup_file(state):
    state.add_user("tim", 6, [56, 76])
    user = state.get_user(0)
    user.generate_client_setup_file()
    setup_file_path = "user_setups/client_setup_{}_{}.json".format(user.user_id, user.user_name)
    setup, server_ip, auth_port = load_setup(setup_file_path)
    os.remove(setup_file_path)
    assert setup.user_id == user.user_id
    assert user.user_name == setup.user_name
    assert user.symm_key == setup.symm_key
    assert state.auth_port == auth_port
    assert state.server_ip == server_ip

def load_setup(setup_file):
    with open(setup_file, "r") as f:
        client_info = json.load(f)
        user_info = client_info["user"]
        user_setup = ServerStateUser(user_id=user_info["user_id"],
                                user_name=user_info["user_name"],
                                ports=user_info["ports"],
                                n_tickets=user_info["n_tickets"],
                                secret=base64.b64decode(user_info["secret"]),
                                symm_key=base64.b64decode(user_info["symm_key"]))
        server_ip = client_info["server_ip"]
        auth_port = client_info["auth_port"]
        return user_setup, server_ip, auth_port
