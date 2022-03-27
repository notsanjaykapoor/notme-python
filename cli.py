import typer

from sqlmodel import Session, SQLModel
from database import engine

from models import user
from services.users.create import Create as UserCreate
from services.users.get import Get as UserGet
from services.users.list import List as UsersList

app = typer.Typer()

@app.command()
def hello(name: str):
  typer.echo(f"Hello {name}")


@app.command()
def goodbye(name: str, formal: bool = False):
  if formal:
    typer.echo(f"Goodbye Ms. {name}. Have a good day.")
  else:
    typer.echo(f"Bye {name}!")


@app.command()
def user_create(name: str):
  typer.echo(f"user {name} create try")

  with Session(engine) as session:
    user = UserGet(session, name).call()

    if user:
      typer.echo(f"user {name} exists")
      return 0

    user_id = UserCreate(session, name).call()

    typer.echo(f"user {name} created")

    return user_id

@app.command()
def user_search(query: str):
  typer.echo(f"user search {query}")

  with Session(engine) as session:
    service = UsersList(session, query, 0, 10)
    struct = service.call()

    for user in struct.users:
      typer.echo(f"user {user}")

if __name__ == "__main__":
  app()
