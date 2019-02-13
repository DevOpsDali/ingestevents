# IngestEvents
This is an example implementation of a Django REST API that ingests a GET/POST to the /loggly endpoint, processes the record, and posts it to the DataDog Event API

## Configuration
There is an example vars.env in the top level of the repository. This file gets passed into the container to control some basic configuration.
Below is an outline of the values:
- SECRET_KEY=SECRET_PLACE_HOLDER - This doesn't need to be changed but should be updated before being used in a production capacity
- DD_API_KEY=DD_API_KEY_PLACE_HOLDER - Update with a valid DataDog API Key
- DD_APP_KEY=DD_APP_KEY_HOLDER - Update with a valid DataDog APP Key.
- DEBUG=True - Controls the Django DEBUG flag in settings.py
- LOG_LEVEL=DEBUG - Controls the log level of the application

Note: The application will still accept and save Loggly requests without the DataDog keys but will be unable to post them to DataDog. There is currently no mechanism to retry posting events in the database

## Usage
The Makefile at the top level of the repository accepts the following commands
- docker - Simply builds the container
- docker-run - Builds and runs the application in a container
- docker-run-d - Same as above but will run the container detached
- docker-shell - Builds the container and overrides the entrypoint with /bin/bash to drop you into a shell
- docker-test - Builds the container and executes the Django test runner