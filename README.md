# Magplan

Project management system for publishers, magazines and content creators, written on the top of Django Framework.

## Features

* complete posts management: from article idea to publishing;
* articles stages, assignees, roles;
* posts metadata, editors, authors, attachments (images, PDF's, files);
* extendable Markdown engine with ability to use external one;
* posts ideas with voting system;
* discussions, email notifications;
* team actions logs;
* publish content to S3 and WordPress with async tasks.

![](docs/screenshot1.jpg)

## Install and run

1. Create new Django project and first app according to official Django [Writing your first Django app, part 1](https://docs.djangoproject.com/en/3.2/intro/tutorial01/) tutorial.
2. Install `django-magplan` with your favourite package management tool: 
    ```
    pip install django-magplan
    ```
    
    or
    
    ```
    pipenv install django-magplan
    ```
   Don't forget to setup database, which is described in Django [Writing your first Django app, part 2](https://docs.djangoproject.com/en/3.2/intro/tutorial02/) tutorial, part 2.
3. Add Magplan to Django `INSTALLED_APPS` in your projects Django `settings.py`. Magplan need some extra requirements, so you should add it too:

    ```
    INSTALLED_APPS = [
      ...
      # Theese apps will be installed with magplan, add it
      'django_ace',
      'django_admin_listfilter_dropdown',
      'dynamic_preferences',
      'dynamic_preferences.users.apps.UserPreferencesConfig',
      'widget_tweaks',
      
      # Add magplan itself
      'magplan',
    ]
    ```
4. Add Magplan to Django in your project `urls.py`:
    ```
    urlpatterns = [
        ...    
        path('plan/', include('magplan.urls')),
        
    ]
    ```
5. Add magplan required middleware to handle multisite:
   ```
   MIDDLEWARE += [
       ...
       'magplan.middleware.SetLanguageMiddleware',
   ]
   ```

6. Add several template context processors for proper rendering last issues, etc:
   ```
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [BASE_DIR / 'templates'],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   # ...Add theese lines to the end
                   'dynamic_preferences.processors.global_preferences',
                   'magplan.context_processors.inject_last_issues',
                   'magplan.context_processors.inject_sites',
               ],
           },
       },
   ]
   ```
7. Run migrations:
   ```
   ./manage.ru migrate
   ```
   Please, refer to Django [Writing your first Django app, part 2](https://docs.djangoproject.com/en/3.2/intro/tutorial02/) tutorial, part 2.

8. Run app:
   ```
   ./manage.py runserver 8080
   ```
4. Go to `http://localhost:8080/plan/`.


Magplan requires Python 3.6+ and Postgres for minimal setup.

Please, note you **must** be authenticated in Django app as each Magplan View is protected by `@login_requred` decorator.

## Deploy with Ansible (deprecated in v2)

_Removed from v2. See  v1 branch_ 

To deploy Magplagn to DEB-based VPS, a complete set of Ansible roles is provided. It includes:

* OS base updates;
* install pip, virtualenv, PosgtreSQL, nginx;
* SSL-certificates by LetsEncrypt with auto-updates;
* Django worker with supervisord and gunicorn.

For more info, please, refer to `ansible/` directory. For regular deploy:

1. Ensure you have `ansible` and `ansible-playbook` installed.
2. Specify Magplan deploy env vars in `ansible/secret_vars/production`:
    ```
    github_secret_token: "<edit_this>"
    postgresql_password: "<edit_this>"
    secret_key: "<edit_this>"
    ```
    
    and [Let’s Encrypt](https://letsencrypt.org/) vars `ansible/group_vars/production`:
    
    ```
    environment_type:
    domain_name:
    letsencrypt_email:
    ```
3. Add your host to `/etc/ansible/hosts` like:
    ``` 
    [control]
    magplan_live ansible_host=magplan.example.com ansible_user=ubuntu
    ``` 
4. Run `ansible-playbook ansible/main.yml`
6. Go to `https://<your_host>:80/` and import test site or create single superuer.

### Running locally

To run Magplan, the following env vars should be set for Python interpreter and Celery worker:

Example settings:

* `DJANGO_SETTINGS_MODULE`: `magplan.settings`
* `BASE_DIR`: `/home/user/code/magplan`
* `DB_HOST`: `localhost`
* `DB_PORT`: `5432`
* `DB_NAME`: `magplan_dev`
* `DB_USER`: `magplan_user`
* `DB_PASSWORD`: `secretpass`
* `APP_HOST`: `localhost`
* `APP_URL`: `http://localhost:8000`
* `APP_ENV`: `DEVELOPMENT`

Install requirements:

```
pip install -r requirements/base.txt
```

Run app:

```
django-admin runserver 0.0.0.0:8000
```

If you plan to run tests, please ensure your user has permissions to create databases.

### Importing test site (deprecated in v2)

To import test site in dev environment, run:

```
manage.py loaddata plan/fixtures/db_test.json.json
```

Login as superuser: `alexander72@example.com:pass123`.

More information can be found [here](https://docs.djangoproject.com/en/2.1/howto/initial-data/). 

### Configuration (deprecated in v2)

After importing test site, please go to `<your_domain>/manage/constance/config/` and set up at least:

* General settings
* Plan email settings
* Finance email settings

These settings are required for proper work. Plan and email settings can be duplicated.

## Todo

* Write more tests
* Complete translations
* Switch to Class-based views
* Rewrite as pluggable app

## LICENSE

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
