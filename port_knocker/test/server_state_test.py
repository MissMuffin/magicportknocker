import base64
import shutil
import uuid

import pytest

from port_knocker.util.auth import generate_secret
from port_knocker.util.server_state import *


@pytest.fixture
def state():
    filename = str(uuid.uuid4()) + ".json"
    state = ServerState(_savefile=filename, server_ip="localhost", auth_port="7889")
    state.remove_all_users()
    yield state
    os.remove(filename)


def test_create_and_save(state):
    state.save()
    print(state._savefile)
    loaded = ServerState(_savefile=state._savefile)
    loaded.load()
    assert loaded.id_count == 0 and isinstance(loaded.users, list)
    assert state.id_count == loaded.id_count and state.users == loaded.users
    assert state.server_ip == loaded.server_ip


def test_add_one(state):
    state.add_user("tim", 10, [1, 2, 3])
    assert state.users[0].user_name == "tim"
    assert state.id_count == 1


def test_add_one_and_load(state):
    state.add_user("tim", 10, [1, 2, 3])
    tim = state.get_user(0)
    loaded = ServerState(_savefile=state._savefile)
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

    loaded = ServerState(_savefile=state._savefile)
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
    user.generate_client_setup_file(state.server_ip, state.auth_port)
    setup_file_path = "user_setups/{}_{}/setup_file.json".format(user.user_name, user.user_id)
    setup, server_ip, auth_port = load_setup(setup_file_path)
    shutil.rmtree("user_setups/{}_{}".format(user.user_name, user.user_id))
    assert setup["user_id"] == user.user_id
    assert user.user_name == setup["user_name"]
    assert user.symm_key == setup["symm_key"]
    assert state.auth_port == auth_port
    assert state.server_ip == server_ip

def test_update(state):
    state.add_user("tim", 6, [56, 76])
    user =  state.get_user(0)
    user.generate_client_setup_file(state.server_ip, state.auth_port)
    setup_file_path = "user_setups/{}_{}/setup_file.json".format(user.user_name, user.user_id)
    setup, _, _ = load_setup(setup_file_path)

    new_ports = [90, 89]
    new_symm = generate_secret()
    state.update_user(user.user_id, new_ports=new_ports, new_symm_key=new_symm)

    updated_setup, _, _ = load_setup(setup_file_path)
    shutil.rmtree("user_setups/{}_{}".format(user.user_name, user.user_id))

    assert setup["user_id"] == updated_setup["user_id"]
    assert updated_setup["ports"] == new_ports
    assert setup["ports"] != updated_setup["ports"]
    assert updated_setup["symm_key"] == new_symm
    assert setup["symm_key"] != updated_setup["symm_key"] 

def load_setup(setup_file):
    with open(setup_file, "r") as f:
        client_info = json.load(f)
        user_info = client_info["user"]
        user_setup = {  "user_id": user_info["user_id"],
                        "user_name": user_info["user_name"],
                        "ports": user_info["ports"],
                        "n_tickets": user_info["n_tickets"],
                        "secret": base64.b64decode(user_info["secret"]),
                        "symm_key": base64.b64decode(user_info["symm_key"])
                }
        server_ip = client_info["server_ip"]
        auth_port = client_info["auth_port"]
        return user_setup, server_ip, auth_port
