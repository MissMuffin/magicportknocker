import click
import requests
from server_state import ServerState

class User():
    user_id = 0
    user_name = ""
    n = 0
    signing_key = b""
    secret = b""
    privilege = ""  # list of ports
    verification_key = b""

    def __init__(self, user_id, user_name, n=10, signing_key=b"", verification_key=b"", secret=b"", privilege=""):
        self.user_id = user_id
        self.user_name = user_name
        self.n = n
        self.signing_key = signing_key
        self.verification_key = verification_key
        self.secret = secret
        self.privilege = privilege 

    def get_server_config(self):
        return {"user_id": self.user_id,
                "user_name": self.user_name,
                "n": self.n,
                "privilege": self.privilege,
                "verification_key": self.verification_key.decode()}

    def get_user_setup(self):
        return {"user_id": self.user_id,
                "privileges": self.privilege,
                "n": self.n,
                "secret": self.secret.decode(),
                "signing_key": self.signing_key.decode()}

test = "hello"

@click.group()
def main():
    """
    \b
    Simple CLI for admin crud operations:
        add user
        view users
        remove user
        generate user setup files
    """
    pass



@main.command()
def add():
    """Add a user and their privileges."""
    user_name = click.prompt("Enter user name (Spaces allowed)")
    ports = click.prompt("Enter port priviliges for user {} (separate port numbers with space)".format(user_name))
    ports = ports.split()
    click.echo("Added {} with {} priviliges: {}".format(user_name, len(ports), ports))
    pass

@main.command()
def view():
    """View all users and their priviliges."""
    click.echo(test)
    pass

@main.command()
@click.argument('id')
def remove(id):
    """Remove user with corresponding id."""
    click.echo("SHOW USER INFO HERE. ID: {}".format(id))
    if click.confirm("Remove this user?"):
        click.echo("Removed user.")        
    pass

@main.command()
def remove_all():
    """Remove all users."""
    if click.confirm("Remove all users?"):
        click.echo("Removed all users.")

@main.command()
def generate():
    """Generate user setup files."""
    pass

if __name__ == "__main__":
    main()