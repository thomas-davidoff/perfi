from tests.factories import UserFactory


async def test_create_user(db_session):
    user = await UserFactory.create(db_session, username="testuser")
    assert user.username == "testuser"
    assert user.email is not None
