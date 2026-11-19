# Fitness-and-Diet-Tracker

Description


## Installation for Development

This is being developed on Windows

I recommend using VSCode, as it has visual Github Source Control

You must have Docker Desktop installed: https://www.docker.com/products/docker-desktop/?at_exp=DO112.B
You must have NodeJS installed: https://nodejs.org/en/download

Once the Repo is added to VSCode, change the .env passwords to something unique.

Next, you must create the python virtual environment and the MySQL Docker Container.

#### 1. Python Virtual Environment
Make sure you have execution rights before you try to run these. 
(See https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.6)

Run the following commands from the Root directory

Create the Virtual Environment
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Open the Virtual Environment
```
.\.venv\Scripts\Activate.ps1
```

Add Dependencies
```
pip -m install -r requirements.txt
```

#### 2. MySQL Docker Container

The container creates the MySQL tables based on /database/schema.sql and populates it with /database/seed.sql

Run this command to create the Docker Container and run it(This may take a couple seconds the first time)

```
docker compose up -d
```

Other Important commands for Database Management

| Command |	Effect |
| -------- | -------- |
| docker compose up -d | Start MySQL |
| docker compose stop |	Stop MySQL |
| docker compose down	| Remove the container and network, preserve the database volume |
| docker compose logs db |	View MySQL logs |
| docker compose down -v	| Remove containers and delete the database volume |

To access SQL from the terminal, run this command and input the password you set in .env
```
docker exec -it fitness_mysql mysql -u fitness_user -p fitness_tracker
```

## Running the Backend

To run the application, execute this command from the root directory
```
python -m backend.app
```

The docker container must be running for the application to work

## Running the Frontend

To run the frontend, Use a different terminal to navigate to /frontend 
```
cd frontend
```

Install dependencies 
```
npm ci
```

Run the frontend using this command
```
npm run dev
```

You should be able to access the frontend UI at http://localhost:5173






