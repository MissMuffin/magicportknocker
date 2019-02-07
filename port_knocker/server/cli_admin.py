import click
from port_knocker.util.server_state import ServerState
from port_knocker.util.auth import generate_secret
from port_knocker.server.admin_core import *
import sys

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

@cli.command()
@click.pass_context
def add(ctx):
    """Add a user and their privileges."""
    state = ctx.obj['state']
    
    # probably first command to be run, so ask to configure server ip and auth port 
    if state.server_ip == "" and state.auth_port == "":
        click.echo("Server info is not configured. Please enter:")
        new_server_ip, new_auth_port = setup_server(state)
        state.server_ip = new_server_ip
        state.auth_port = new_auth_port

    user_name = prompt_username()
    n_tickets = click.prompt("Enter number of tickets for this user", type=int, default=3)
    ports = prompt_port_numbers(user_name)
    state.add_user(user_name=user_name, n_tickets=n_tickets, ports=ports) 
    click.echo("Added {} ticket(s) for user {} with {} priviliges: {}".format(n_tickets, user_name, len(ports), ports))
        
@cli.command()
@click.pass_context
def view(ctx):
    """View all users and their priviliges."""
    state = ctx.obj['state']
    show_server_config(state.server_ip, state.auth_port)
    show_user_table(state.users)

@cli.command()
@click.argument("id", required=True, type=int)
@click.pass_context
def remove(ctx, id):
    """Remove user with corresponding id."""
    state = ctx.obj['state']
    user = state.get_user(int(id))
    # validate id
    if user == None:
        click.echo("No user with this id.")
    else:
        show_user_table(user)
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

@cli.command()
@click.argument('id', required=True, type=int)
@click.pass_context
def update(ctx, id):
    """Edit a user's port privileges and/or generate new symmetric key."""
    state = ctx.obj['state']
    user = state.get_user(int(id))
    # validate id
    if user == None:
        click.echo("No user with this id.")
    else:
        # update ports
        new_ports = get_new_ports(user.ports, user.user_name)

        # update symm_key
        new_symm_key = user.symm_key
        if click.confirm("Generate new symmetric key for this user?"):
            new_symm_key = generate_secret()

        # check for changes
        if new_ports == user.ports and new_symm_key == user.symm_key:
            # nothing was changed, exit without updating
            click.echo("User remains unchanged.")
            sys.exit(0)

        state.update_user(user.user_id, new_ports=new_ports, new_symm_key=new_symm_key)
        click.echo("Data has been saved and new user setup file has been generated.")

@cli.command()
@click.pass_context
def configure(ctx):
    """
    Enter the ip address of the server and the port for authentication that user
    will use.
    """
    state = ctx.obj['state']
    update_server(state)

def main():
    cli(obj={})

if __name__ == "__main__":      
    main()