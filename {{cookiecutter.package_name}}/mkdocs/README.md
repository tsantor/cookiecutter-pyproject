# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Run the Docker Container

    docker-compose up

If you have not run `docker-compose build` or `docker-compose up` before, it will first build the image which will take some time. After it's built `docker-compose up` should take seconds to get you up and running.

## Visit the Docs
Open [http://localhost:8989](http://localhost:8989) in your browser.

## Building your site
With the Docker container running, run the following in another terminal from within the project directory:

```bash
make build
```

## Deploy
With the Docker container running, run the following in another terminal from within the project directory:

```bash
make deploy
```

**Note:** You will need your SSH key on the server in order to do this step.
