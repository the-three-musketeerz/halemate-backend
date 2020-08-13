# haleMate

## Setup
- Prerequisites:
  - Python 3
  - pip
  - MySql
  - default-libmysqlclient-dev

- Install the following for Knox setup
```
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev python-dev

```

- Clone this repository.

- Set up a virtual environment.
```
python3 -m venv halemate_env
```

- Activate the virtual environment.
```
source halemate_env/bin/activate
```

- Create a MySql database named halemateDB.

- Navigate inside the cloned repository and install the required dependencies using the command:
```
pip install -r requirements.txt
```

- Navigate to /halemate_backend and create a file named .env and store the following credentials inside it
```
SECRET_KEY=your-secret-key

DATABASE_USER=mysql-database-username
DATABASE_PASSWORD=mysql-database-password

FCM_SERVER_KEY=fcmserverkey

EMAIL_ID=email_id
EMAIL_PASSWORD=email_password
```

- Navigate back to the base directory for the app where <span>manage.py</span> file is located and make the database migrations using following command:
```
python manage.py migrate
```

- Start a Redis server on port 6379 using the following command:
```
docker run -p 6379:6379 -d redis:5
```

- Start the backend server:
```
python mange.py runserver
```