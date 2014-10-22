## Requirements
This application was developed and tested on:

* Django 1.7
* celery==3.1.15
* Python 2.7


## Configuration
1. Setup Celery BROKER_URL (conf/celery_conf.py)
    ```python
        BROKER_URL = 'amqp://guest:guest@localhost:5672//'
    ```

2. Setup Email settings (conf/email.py)

    ```python
        EMAIL_HOST = 'smtp.gmail.com'
        EMAIL_HOST_USER = '__MAILBOX__@gmail.com'
        EMAIL_HOST_PASSWORD = '********'
        EMAIL_PORT = 587
    ```
    If EMAIL_HOST is Gmail check mail settings at `https://www.google.com/settings/security/lesssecureapps`

3. Setup DATABASES settings (settings.py)

4. Run command: `pip install -r requirements.txt`




## Start
```python
# activate virtualenv
```
1. Run command: `python manage.py syncdb`
2. Run command: `python manage.py collectstatic`
3. Run `run_celery.sh` script to start celery worker: `. ./run_celery.sh`
3. Run command: `python websocket.py`
4. Run command: `python manage.py runserver`
5. Open browser at 127.0.0.1:8000