# Readme placeholder
I forgot alot of the things I've already done, so just an outline:
- create env file
- outline the configuration stuff - setting up env file, config.py file, flask env, etc
- required variables to start - secret key, flask env, db uri etc

Database setup
- postgres
- configuration
- create db prior to starting app or use db_admin cli tools with superuser (i should probably delete that - horrible choice)

Testing
Contributing (as if anyone's gonna contribute lmao)


`pip install -r requirements.txt`
Set up pre-commits for Black formatting
`pre-commit install`
Will set up the pre-commit hook for formatting. Whitespace, yml, black.

Run the hooks when adding:
`pre-commit run --all-files`


Using flask jwt
add JWT_SECRET_KEY to env file
