import pytest
from alembic.script import Script, ScriptDirectory
from config.migrations import alembic_config, run_upgrade, run_downgrade


def get_revisions():
    revisions_dir = ScriptDirectory.from_config(alembic_config)
    revisions = list(revisions_dir.walk_revisions("base", "heads"))
    revisions.reverse()
    return revisions


@pytest.mark.parametrize("revision", get_revisions())
async def test_migrations_stairway(revision: Script, sessionmanager_for_tests):
    async with sessionmanager_for_tests.connect() as conn:
        await conn.run_sync(run_upgrade, alembic_config, revision.revision)
    async with sessionmanager_for_tests.connect() as conn:
        await conn.run_sync(
            run_downgrade, alembic_config, revision.down_revision or "-1"
        )
        await conn.run_sync(run_upgrade, alembic_config, revision.revision)
