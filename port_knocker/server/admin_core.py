import click
from terminaltables import AsciiTable
import ipaddress

def prompt_username():
    blacklisted_characters = ['/', '\\', '.']
    user_name = click.prompt("Enter user name (Spaces allowed)").strip()
    if user_name == "":
        click.echo("Input was empty.")
        return prompt_username()
    if any(c in user_name for c in blacklisted_characters): 
        print("{} contains illegal characters ({})".format(user_name, blacklisted_characters))
        return prompt_username()
    return user_name

def prompt_port_numbers(user_name):
    ports = click.prompt("Enter port priviliges for user {} (separate port numbers with space)".format(user_name))
    ports = ports.strip().split()
    if ports == []:
        click.echo("Input was empty.")
        return prompt_port_numbers(user_name)
    try:
        if any(int(port) > 65535 or int(port) < 1 for port in ports):
            click.echo("Invalid port numbers, needs to be between 1 and 65535")
            return prompt_port_numbers(user_name)
    except ValueError:
        click.echo("Ports must be integers")
        return prompt_port_numbers(user_name)
    return ports

def get_new_ports(old_ports, user_name):
    click.echo("The user {} currently has the following port privileges: {}.".format(user_name, str(old_ports)))
    click.echo("Enter new port priviliges (separate port numbers with space).")
    ports = click.prompt("To keep old port privileges, press enter without inputting anything.", default="", show_default=False).strip()

    # check if keep old ports
    if ports == "":
        return old_ports

    # validate new ports
    ports = ports.split()
    try:
        if any(int(port) > 65535 or int(port) < 1 for port in ports):
            click.echo("Invalid port numbers, needs to be between 1 and 65535")
            return get_new_ports(old_ports, user_name)
    except ValueError:
        click.echo("Ports must be integers")
        return get_new_ports(old_ports, user_name)
    return ports

def validate_ipv4_address(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False

def prompt_server_ip(old_server_ip, allow_old):
    msg = "Enter new server address."
    if allow_old:
        msg.join("\nLeave empty and press enter to keep old address.")
        new_server_ip = click.prompt(msg, default="", show_default=False, type=str).strip()
    else:
        new_server_ip = click.prompt(msg, type=str).strip()
    
    # check if was empty
    if new_server_ip == "":
        if allow_old:
            new_server_ip = old_server_ip
        else:
            click.echo("Input was empty.")
            return prompt_server_ip(old_server_ip, allow_old)
    else:
        is_valid_ip = validate_ipv4_address(new_server_ip)
        if not is_valid_ip:
            click.echo("{} does not appear to be an IPv4 address. Enter valid IP.".format(new_server_ip))
            return prompt_server_ip(old_server_ip, allow_old)
    return new_server_ip

def prompt_auth_port(old_auth_port, allow_old):
    msg = "Enter new authentication port."
    if allow_old:
        msg.join("\nLeave empty and press enter to keep old port.")
        new_auth_port = click.prompt(msg, default="", show_default=False, type=int)
    else:
        new_auth_port = click.prompt(msg, type=int)

    # check if empty -> keep old
    if new_auth_port == "":
        if allow_old:
            new_auth_port = old_auth_port
        else:
            click.echo("Input was empty.")
            return prompt_auth_port(old_auth_port, allow_old)
    else:
        # validate
        if new_auth_port > 65535 or new_auth_port < 1 :
            click.echo("Invalid port number, needs to be between 1 and 65535")
            return prompt_auth_port(old_auth_port, allow_old)
    return new_auth_port

def setup_server(state):
    click.echo("Server info is not configured. Please enter:")

    new_server_ip = prompt_server_ip(state.server_ip, allow_old=False)
    new_auth_port = prompt_auth_port(state.auth_port, allow_old=False)

    if not click.confirm("Configuration: {}:{}. Save?".format(new_server_ip, new_auth_port)):
        return setup_server(state)

    state.server_ip = new_server_ip
    state.auth_port = new_auth_port
    state.save()
    click.echo("Updated server config successfully.")
    return state

def configure_server(state):
    click.echo("Current configuration:")
    show_server_config(state.server_ip, state.auth_port)

    new_server_ip = prompt_server_ip(state.server_ip, allow_old=True)
    new_auth_port = prompt_auth_port(state.auth_port, allow_old=True)
    
    # confirm configuration
    confirm = click.confirm("New configuration: {}:{}. Save?".format(new_server_ip, new_auth_port))
    if confirm:
        state.server_ip = new_server_ip
        state.auth_port = new_auth_port
        state.generate_all_client_setup_files()
        state.save()
        click.echo("Updated server config successfully and updated all user setup files")    
    else:
        click.echo("Server config unchanged.")

def show_user_table(users):
    data = []
    data.append(["Id", "User name", "Remaining tickets", "Ports"])
    
    if isinstance(users, list):
        if len(users) > 0:
            for user in users:
                data.append([user.user_id, user.user_name, user.n_tickets, " ".join(user.ports)])
        else:
            data.append(["", "", "", ""])
    else:
        data.append([users.user_id, users.user_name, users.n_tickets, " ".join(users.ports)])

    table = AsciiTable(data)
    click.echo(table.table)

def show_server_config(server_ip, auth_port):
    data = []
    data.append(["Server IPv4 address", "Authentication port"])
    data.append([server_ip, auth_port])
    table = AsciiTable(data)
    click.echo(table.table)