import click
import requests
from port_knocker.util.server_state import ServerState
from terminaltables import AsciiTable

state = None # type: ServerState

@click.group()
@click.pass_context
def cli(ctx):
    """
    \b
    Simple CLI for admin crud operations:
        add user
        view users
        remove user
        generate client setup files for users
    """
    state = ServerState()
    try:
        state.load()
    except:
        pass
    ctx.obj['state'] = state

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

def getValidUsername():
    blacklisted_characters = ['/', '\\', '.']
    user_name = click.prompt("Enter user name (Spaces allowed)")
    if any(c in user_name for c in blacklisted_characters): 
        print("{} contains illegal characters ({})".format(user_name, blacklisted_characters))
        return getValidUsername()
    return user_name

def getPortNumbers(user_name):
    ports = click.prompt("Enter port priviliges for user {} (separate port numbers with space)".format(user_name))
    ports = ports.split()
    try:
        if any(int(port) > 65535 or int(port) < 1 for port in ports):
            click.echo("Invalid port numbers, needs to be between 1 and 65535")
            return getPortNumbers(user_name)
    except ValueError:
        click.echo("Ports must be integers")
        return getPortNumbers(user_name)
    return ports

@cli.command()
@click.pass_context
def add(ctx):
    """Add a user and their privileges."""
    user_name = getValidUsername()
    n_tickets = click.prompt("Enter number of tickets for this user", type=int, default=3)
    ports = getPortNumbers(user_name)
    ctx.obj['state'].add_user(user_name=user_name, n_tickets=n_tickets, ports=ports) 
    click.echo("Added {} ticket(s) for user {} with {} priviliges: {}".format(n_tickets, user_name, len(ports), ports))
        

@cli.command()
@click.pass_context
def view(ctx):
    """View all users and their priviliges."""
    state = ctx.obj['state']
    _show_user_table(state.users)

@cli.command()
@click.argument("id")
@click.pass_context
def remove(ctx, id):
    """Remove user with corresponding id."""
    state = ctx.obj['state']
    user = state.get_user(int(id))
    # validate id
    if user == None:
        click.echo("No user with this id.")
    else:
        _show_user_table(user)
        if click.confirm("Remove this user?"):
            state.remove_user_by_id(user.user_id)
            click.echo("Removed user {}.".format(user.user_name)) 

@cli.command()
@click.pass_context
def remove_all(ctx):
    """Remove all users."""
    state = ctx.obj['state']
    n_users = len(state.users)
    if click.confirm("Remove all users? (Currently {} users)".format(n_users)):
        state.remove_all_users()
        click.echo("Removed {} users.".format(n_users))


def main():
    cli(obj={})

if __name__ == "__main__":      
    main()