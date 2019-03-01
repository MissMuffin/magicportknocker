import uuid

import pytest

from port_knocker.util.client_state import *
from port_knocker.util.server_state import *


@pytest.fixture
def server_state_setup():
    filename = str(uuid.uuid4()) + ".json"
    setup_file_path = str(uuid.uuid4()) + ".json"
    server_state = ServerState(_savefile=filename)
    server_state.remove_all_users()
    server_state.add_user("karl", 100, [2, 44])
    user = server_state.get_user(0)
    setup_data = {}
    setup_data["user"] = user.get_client_setup_dict()
    setup_data["server_ip"] = "SERVER_IP"
    setup_data["auth_port"] = 123
    with open(setup_file_path, "w+") as f:
        json.dump(setup_data, f)
    yield (server_state, setup_file_path)
    os.remove(filename)
    os.remove(setup_file_path)

@pytest.fixture
def client_state(server_state_setup):
    _, setup_file_path = server_state_setup
    client_state = ClientState._load(setup_file_path)
    return client_state    

def test_import_setup(server_state_setup):
    server_state, setup_file_path = server_state_setup
    client_state = ClientState._load(setup_file_path)
    user = server_state.get_user(0)
    assert client_state.user_name == user.user_name
    assert client_state.symm_key == user.symm_key

def test_save_load(client_state):
    filename = str(uuid.uuid4()) + ".json"
    client_state._savefile = filename
    client_state.save()
    loaded_client_state = ClientState._load(savefile=filename)
    assert client_state.symm_key == loaded_client_state.symm_key
    assert client_state.ports == loaded_client_state.ports
    assert client_state.auth_port == loaded_client_state.auth_port
    os.remove(filename)
