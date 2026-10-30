# Mister X WebUI NG

Provides a WebUI for a Mister X game, currently provides the ability to manage
points and tasks as the leader of the game.

## Example data

`src/misterx/fixtures` contains example data for development: players and
groups, a task catalogue, three games (a finished one, the active one and a
planned one) and submissions in every review state. Load it into a freshly
migrated database from within `src/`:

```sh
python manage.py loaddata users tasks games submissions
```

All users have the password `misterx`. `admin` and `reviewer` are game leaders,
`alice` to `frank` play in the active game, `grace` only played in the finished
game and `heidi` is deactivated. Never load these fixtures into a production
database.
