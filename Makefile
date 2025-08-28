preview :  
	poetry run python manage.py runserver

mm :
	poetry run python manage.py makemigrations

migrate : 
	poetry run python manage.py migrate

tailwind-build :
	poetry run python manage.py tailwind build

tailwind-start :
	poetry run python manage.py tailwind start
