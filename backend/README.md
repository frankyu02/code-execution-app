# Backend Created using FastAPI and SQLite
The backend has 2 endpoints

```/api/test```
Takes code as a string and executes it and returns all stdout data to the user

```/api/submit```
Takes code as a string and saves the code to a SQLite DB if running code does not cause errors. The Id is automatically generated by the server

```/api/submissions```
Is a GET method that returns all the currently submitted code snippets along with their output 

# Dealing with Malicious Code
The program attempts to reduce any damages from maliciously passed code by

1. Using docker to run the passed in code in a container to ensure that the actual server's hardware is not affected (although there is a chance that the kernel can be attacked since Docker still shares the kernel)
2. Allowing code to only run a specific amount of time (5 seconds in this case). If the allowed execution time is exceeded, it is treated as invalid code. This prevents resource-based attacks such as just simply having an infinite loop run on the server to decrease the total resources that server has

# Running the backend
Install the required packages using

```pip install fastapi uvicorn sqlalchemy psycopg2-binary docker```

[You must also have Docker installed](https://docs.docker.com/engine/install/)

Run the program with ```uvicorn main:app```

It will run on ```localhost:8000``` by default

## Notes about the backend:
The backend uses docker to execute the code. The backend of capable of creating this image when the API is initially called however this process can be lengthy. You can speed up the API beforehand by installing the docker image. A dockerfile is provided in the backend directory. Please run

```python-execution-environment:3.11```

To create the image. **This is only to improve the initial execution speed**
