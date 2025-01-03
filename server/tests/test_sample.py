async def test_create_user(db_session):
    from tests.helpers.factories import UserFactory

    user = await UserFactory.create(db_session, username="testuser")
    assert user.username == "testuser"
    assert user.email is not None
