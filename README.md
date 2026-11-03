# Fitness-and-Diet-Tracker

Description


## Installation for Development

This is being developed on Windows
I recommend using VSCode, as it has visual Github Source Control
You must have Docker Desktop installed: https://www.docker.com/products/docker-desktop/?at_exp=DO112.B

Once the Repo is added to VSCode, you must create the python virtual environment and the Docker Container.

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






