# Theatre API Service

The Theatre API Service provides a comprehensive platform to manage and access theater-related information and functionalities through a standardized API interface. It enables users to retrieve details about shows, schedules, ticket availability, theater locations, and other relevant data related to theatrical events. This service facilitates easy integration with various applications, allowing developers to access and utilize theater-related data seamlessly for diverse purposes such as ticket booking, event scheduling, and more.

## Initialize locally
Install PostgresSQL and create db.

1. Clone the repository:
```
git clone https://github.com/Oxbay/Theatre-API-Service.git
```
2. Navigate to the project directory:
```
cd theatre_api_service
```

3. Switch to the develop branch:
```
git checkout develop
```
4. Create a virtual environment:
```
python -m venv venv
```
5. Activate the virtual environment:

On macOS and Linux:
```
source venv/bin/activate
```
On Windows:
```
venv\Scripts\activate
```
6. Install project dependencies:
```
pip install -r requirements.txt
```
7. Copy .env.sample to .env (you must make it) and fill it with all required dat

8. Run database migrations:
```
python manage.py migrate
```
9. Start the development server:
```
python manage.py runserver
```

## Run with Docker
Docker should be installed.

+ pull docker container
``` 
docker pull oxbay/docker-theatre
```
+ run container
```
docker-compose build
docker-compose up
```

## Getting access
+ Create user: `/api/user/register/`
+ Get access token: `/api/user/token/`
+ Look for documentation: `/api/doc/swagger/`
+ Admin panel: `/admin/`

## Features
+ JWT Authentication
+ Email-Based Authentication
+ Admin panel
+ Pagination for all pages
+ Throttling Mechanism
+ API documentation
+ Upload image to Play
+ Filtering Plays by genres
+ Managing reservations and tickets
