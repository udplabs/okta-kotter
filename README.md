## python-okta-multidemo

### Run locally

```
git clone https://github.com/mdorn/python-okta-multidemo
cd python-okta-multidemo
python3 -m venv env
. env/bin/activate
pip install -r requirements.txt
cp .env.example .env  # modify your .env file with values for your Okta environment
flask run
```

### Run in Docker container

```
docker pull mdorn/okta-multidemo
docker run --env-file PATH_TO_YOUR_ENV_FILE --name okta-multidemo -p 5000:5000 mdorn/okta-multidemo
```

### Acknowledgments

- Bank image by Adrien Coquet from the Noun Project
