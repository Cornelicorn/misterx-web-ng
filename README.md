# Mister X WebUI NG

Provides a WebUI for a Mister X game, currently provides the ability to manage
points and tasks as the leader of the game.

## Dependencies

The layout, the generic pages, the theme switcher and the account pages come
from the app `tabler_ui`, the user preferences, which keep the theme of logged
in users, and the SSO login from the app `volucra_base`. Both are in the
private repository [volucra-django-base](https://github.com/Cornelicorn/volucra-django-base).
`uv sync` installs it from GitHub, so the machine needs read access to that
repository, e.g. through an SSH key or a token in the git credentials. The
commit it is pinned to is set in `[tool.uv.sources]` of `pyproject.toml`.

The templates in `src/templates/tabler_ui` extend the ones of `tabler_ui` to
add the navbar entries and the stylesheet of Mister X.

Mister X needs Python 3.12 (Ubuntu 24.04) or newer. Dependabot updates
`uv.lock` weekly. The lower bound of each dependency is the version Mister X
is tested with, the upper bound the next version which may break it according
to the versioning of that project, see the dependency updates in the README of
volucra-django-base. Dependabot raises it when a version beyond it comes out.
To resolve volucra-django-base it needs the Dependabot secret
`VOLUCRA_DJANGO_BASE_TOKEN`, a token with read access to the contents of that
repository.

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
