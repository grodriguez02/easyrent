export PGDATABASE := tfg
export PGUSER := guilleadmin
export PGPASSWORD := guilleadmin
export PGCLIENTENCODING := LATIN9
export PGHOST := localhost
PSQL = psql

CMD = python3 manage.py
HEROKU = heroku run export SQLITE=1 &


run:
	$(CMD) runserver

reset_db: clear_db update_db create_super_user

clear_db:
	@echo Clear Database
	dropdb --if-exists $(PGDATABASE)
	createdb

shell:
	@echo create psql shell
	@$(PSQL)

populate:
	@echo populate database
	python3 ./manage.py populate

update_db:
	$(CMD) makemigrations
	$(CMD) migrate

create_super_user:
	$(CMD) shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('guilleadmin', 'a@a.es', 'guilleadmin')"

clear_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations easyrent
	python3 ./manage.py migrate


test_datamodel:
	$(CMD) test core.tests_models
