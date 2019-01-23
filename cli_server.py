import click
import requests
from server_state import ServerState
from terminaltables import AsciiTable

state = None # type: ServerState

@click.group()
def main():
    """
    \b
    Simple CLI for admin crud operations:
        add user
        view users
        remove user
        generate client setup files for users
    """
    pass

def _show_user_table(users):
    data = []
    data.append(["Id", "User name", "Remaining tickets", "Ports"])
    
    if isinstance(users, list):
        for user in users:
            data.append([user.user_id, user.user_name, user.n_tickets, " ".join(user.ports)])
    else:
        data.append([users.user_id, users.user_name, users.n_tickets, " ".join(users.ports)])

    table = AsciiTable(data)
    click.echo(table.table)

@main.command()
def add():
    """Add a user and their privileges."""
    user_name = click.prompt("Enter user name (Spaces allowed)")
    n_tickets = click.prompt("Enter number of tickets for this user", type=int, default=3)
    print(n_tickets)
    ports = click.prompt("Enter port priviliges for user {} (separate port numbers with space)".format(user_name))
    ports = ports.split()
    state.add_user(user_name=user_name, n_tickets=n_tickets, ports=ports) 
    click.echo("Added {} ticket(s) for user {} with {} priviliges: {}".format(n_tickets, user_name, len(ports), ports))

@main.command()
def view():
    """View all users and their priviliges."""
    _show_user_table(state.users)

@main.command()
@click.argument("id")
def remove(id):
    """Remove user with corresponding id."""
    user = state.get_user(int(id))
    # validate id
    if user == None:
        click.echo("No user with this id.")
    else:
        _show_user_table(user)
        if click.confirm("Remove this user?"):
            state.remove_user_by_id(user.user_id)
            click.echo("Removed user {}.".format(user.user_name)) 

@main.command()
def remove_all():
    """Remove all users."""
    n_users = len(state.users)
    if click.confirm("Remove all users? (Currently {} users)".format(n_users)):
        state.remove_all_users()
        click.echo("Removed {} users.".format(n_users))

@main.command()
def generate_all():
    """Generate client setup files for all users. 
    Automatically overwrites old setup files of a user."""
    state.generate_all_client_setup_files()
    click.echo("Client setup files for all users have been generated.")

@main.command()
@click.argument("id")
def generate(id):
    """Generate client setup files for a single user. 
    Automatically overwrites old setup file for this user."""
    user = state.get_user(int(id))
    if user == None:
        click.echo("No user with this id.")
    else:
        user.generate_client_setup_file()
        # TODO error handling?
        click.echo("Client setup file has been generated.")

if __name__ == "__main__":    
    # do setup here for commands
    state = ServerState()
    try:
        state.load()
    except Exception:
        pass
    
    main()