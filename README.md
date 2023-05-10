Hey there! 👋 Welcome to version 3.9 of our awesome Flask web application! 🎉

This version comes with a **Docker Compose file** that defines our Flask app (`flask_app_jru`) and two PostgreSQL database services (`flask_db` and `flask_db_test`) that you can use to run the app locally.

The Flask web app is built using an image (`francescoxx/flask_live_app:1.0.0`) and runs on **port 4000**. The `flask_app_jru` container depends on the `flask_db` service, which uses the PostgreSQL image version 12 and runs on **port 6969**. I also included a second instance of the database service (`flask_db_test`) for testing purposes, which runs on **port 7070**. Both database services use separate volumes (`pgdata` and `pgdata_test`) to store data.

We made things easier for you by setting up some environment variables inside the `flask_app_jru` container. The `DB_URL` variable specifies the connection string to the database service, while `OUTPUT_FILES` specifies the path to the directory where output files are generated. The container also creates a volume (`output_files`) for the output directory and mounts it as a volume inside the container.

## Getting started

To start the app, navigate to the directory containing the Docker Compose file and run the following command:

```bash
docker-compose up
```

This will start all three services (`flask_app_jru`, `flask_db`, and `flask_db_test`) and initialize the database volumes. The Flask web application will be accessible at http://localhost:4000. 

To stop the app, press `CTRL+C` in the terminal where the Docker Compose command is running, or run the following command:

```bash
docker-compose down
```

This will stop and remove all three services and their associated containers and volumes.

Here's how you can connect to the `flask_db` PostgreSQL database service from a local database tool:

1. First, make sure the `flask_db` service is running by running `docker-compose up` in the directory containing the Docker Compose file.

2. Open your database tool of choice (e.g. [Postico](https://eggerapps.at/postico/), [pgAdmin](https://www.pgadmin.org/), [DBeaver](https://dbeaver.io/)).

3. Create a new database connection and enter the following details:

   - **Host:** `localhost`
   - **Port:** `6969`
   - **Database:** `postgres`
   - **Username:** `postgres`
   - **Password:** `postgres`

4. Test the connection and make sure you can successfully connect to the database service.

5. You're all set! You can now use your local database tool to interact with the `flask_db` PostgreSQL database service and run queries against it.

Note that if you want to connect to the `flask_db_test` database service for testing purposes, you'll need to use a different port (`7070`) and different username and password (`postgres_test` for both).

**Note:** This Docker Compose file is intended for development and testing purposes only and should not be used in a production environment without proper modifications and security measures. 😎



## Disclaimer: 

Although I could have chosen to work on this project using C#, I decided to challenge myself and learn something new by working with Flask 📚💡🌟. While I acknowledge that C# is a powerful language and could have been used for this project, I wanted to expand my skillset and gain experience with a new technology. 

Please keep in mind that my experience with Flask is limited, and there may be areas where I could have utilized C# more effectively. Nonetheless, I am excited to have had the opportunity to work with Flask and further my knowledge in this area.