import pytest
from client_state import *
from server_state import *
import uuid

@pytest.fixture
def server_state_setup():
    filename = str(uuid.uuid4()) + ".json"
    setup_file_path = str(uuid.uuid4()) + ".json"
    server_state = ServerState(save_file=filename)
    server_state.remove_all_users()
    server_state.add_user("karl", 100, [2, 44])
    user = server_state.get_user(0)
    setup_data = {}
    setup_data["user"] = user.get_client_setup_dict()
    setup_data["server_ip"] = "SERVER_IP"
    setup_data["auth_port"] = "AUTH_PORT"
    with open(setup_file_path, "w+") as f:
        json.dump(setup_data, f)
    yield (server_state, setup_file_path)
    os.remove(filename)
    os.remove(setup_file_path)

# client state
# prepared from setup file import
@pytest.fixture
def client_state(server_state_setup):
    _, setup_file_path = server_state_setup
    client_state = ClientState.load(setup_file_path)
    return client_state    

def test_import_setup(server_state_setup):
    server_state, setup_file_path = server_state_setup
    client_state = ClientState.load(setup_file_path)
    user = server_state.get_user(0)
    assert client_state.user_name == user.user_name
    assert client_state.symm_key == user.symm_key

def test_save_load(client_state):
    filename = str(uuid.uuid4()) + ".json"
    client_state.save(save_file=filename)
    loaded_client_state = ClientState.load(save_file=filename)
    assert client_state.symm_key == loaded_client_state.symm_key
    assert client_state.ports == loaded_client_state.ports
    assert client_state.auth_port == loaded_client_state.auth_port
    os.remove(filename)