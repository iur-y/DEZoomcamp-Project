# What is this repository?
It's my capstone project for the data engineering zoomcamp, a free data engineering course, which can be found [here](https://github.com/DataTalksClub/data-engineering-zoomcamp).
# What is the project about?
An end-to-end batch data pipeline, including extracting, loading and transforming data, which runs 100% in the cloud.

# Diagram
![Diagram](https://github.com/iur-y/DEZoomcamp-Project/blob/main/images/diagram.png?raw=true)

# Data Visualization
![Report](https://github.com/iur-y/DEZoomcamp-Project/blob/main/images/report.png?raw=true)
You can find the Power BI file in the report folder\
Note: the data was generated at random based on a sample file so that I could work with larger datasets in multiple files, which means numbers will vary from run to run

# What technologies does it use?
- Docker for containerization
- Terraform for cloud infrastructure
- Airflow for orchestration
- Google Cloud Platform for cloud services
- dbt for transformations
- Microsoft Power BI for data visualization

# How can I replicate this project?
### I recommend that you read all the steps below from start to finish before replicating them, so you have an idea of what to expect.
### There's also a section at the end which explains the project in detail
0. Use a Unix-like operating system and make sure you have the _sed_ utility program installed
1. Install requirements
    * 1.1 [Docker](https://docs.docker.com/get-docker/)
    * 1.2 [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
2. Make a directory and clone the repository\
`git clone https://github.com/iur-y/DEZoomcamp-Project.git`
3. Create a new Google Cloud project to start fresh. The costs should be less than $1 as of April 2024
    * 3.1 Make sure billing is enabled. You can do so by typing _**Billing projects**_ in the search bar
    * 3.2 Make sure the Service Usage API is enabled. You can do so by typing _**Enabled APIs & services**_ in the search bar. If it is not enabled, click _**ENABLE APIS AND SERVICES**_ and search for _**Service Usage API**_ and enable it
    * 3.3 Copy your Project ID to somewhere as it will be needed later
4. Go to Service Accounts and create a service account as follows:
    * 4.1 Give it a name and click _**CREATE AND CONTINUE**_
    * 4.2 Assign the following roles to it:
        * 4.2.1 Artifact Registry Administrator
        * 4.2.2 BigQuery Admin
        * 4.2.3 Cloud Run Admin
        * 4.2.4 Compute Admin
        * 4.2.5 Cloud Scheduler Admin
        * 4.2.6 Service Account User
        * 4.2.7 Service Usage Admin
        * 4.2.8 Storage Admin
    * 4.3 Click _**DONE**_
    * 4.4 You should see an email address created for the service account that looks like `name@project.iam.gserviceaccount.com`. Copy it to somewhere as it will be needed later
5. Create a key
    * 5.1 Still in the same service accounts page, you can click on the email and it should redirect you to a page where you can then go to _**KEYS**_ > _**ADD KEY**_ > _**CREATE NEW KEY**_ > _**JSON**_ > _**CREATE**_
    * 5.2 Put the key in the _creds_ directory, which is located in the root of the cloned repository
    * 5.3 Rename the key to my-creds.json
6. Replace the project id and service account email
    * 6.1 Edit the _terraform/variables.tf_ file and replace the fields that are commented out, **keep the double quotes but remove the `<` and `>` symbols**
    * 6.2 Uncomment those two lines, it should look like `default = "your_project_id"` and `default = "your_service_account_email"`
7. Run the scripts in order (you might want to monitor them because it's possible that something fails, the script continues running, and you get a false positive message at the end)
    * 7.1 `./pre-init.sh`\
    This is meant to get user input to create the Cloud Storage bucket names, since they have to be globally unique
    * 7.2 `./init1-push.sh`\
        This builds the Docker images and pushes them to Artifact Registry where they are kept. It also uses Terraform to enable the required APIs to do that
    * 7.3 Ideally now you wait until the time is 1 minute before a multiple of 20, i.e. **hh:19 or hh:39 or hh:59** and only then run `./init2-apply.sh`\
        This is because the dbt container runs following the **\*/20 \* \* \* \*** cron expression, and it won't be created and ready to run in just 1 minute (detailed information about the code is in a section below). Anyway, what _init2-apply.sh_ does is create all the order resources with the command _**terraform apply**_, such as the Compute Engine, Cloud Run application, BigQuery dataset and table and Cloud Run Jobs. Note that you will have to type _**yes**_ for confirmation
8. Poke around. Now that every resource is created, you can navigate to their respective pages and see what was created:
    * 8.1 Cloud Storage should have two buckets
    * 8.2 BigQuery should have a dataset and a table (two after the dbt job runs)
    * 8.3 Cloud Run should have the application running
    * 8.4 Cloud Run Jobs should have two jobs listed
    * 8.5 Cloud Scheduler should have one schedule for each Cloud Run Job
9. At **hh:00 or hh:20 or hh:40**, the dbt job will start running and create a second table in BigQuery. After the job concludes (check either on the BigQuery page or Cloud Run Jobs page), run
    * 9.1 `./terminate1.sh`\
    This will terminate all the major billable resources such as the Compute Engine and Cloud Run service, but it keeps the dataset in BigQuery and the Cloud Storage buckets in case you wish to run queries, inspect the data or use a BI tool to create a dashboard
    * 9.2 `./terminate2.sh`
    This does _**terraform destroy**_ and will also ask for input. Enter _**yes**_ for confirmation. After that, you can delete the Google Project should you prefer

# Code, infrastructure and project details

### Code
I like to comment a lot which means you will find many comments in most files should you want to see how something was done

---

### Project
#### <ins>Data Source: app</ins>
I decided to make my own data source instead of using a public API on the internet in order to experiment with API pagination and have more control over the size of the data. This allows me to write code expecting a large response from an API and parse it using generators.

It's a simple Flask application which has been containerized and deployed with Google's Cloud Run service (look for _"google\_cloud\_run\_v2\_service"_ in _terraform/main.tf_). The code is in the _app_ directory. The app has a **/data** endpoint where you make requests with two arguments: _start_ and _end_. Valid values for _start_ are either the string "beginning", which will return all the data that was produced and is in the GCS bucket at the moment of request; or you can also pass an ISO 8601 date format which will return data that was produced after the passed date argument. On the other hand, _end_ is optional and you can only pass ISO 8601 date arguments to it. Its purpose is to limit the amount of returned data. If you don't use _end_, then everything starting from _start_ is returned.

The app reads parquet files from a GCS bucket and returns them as an iterator in pages of 200 records per page.

The _docker_ directory contains the Dockerfile for building the image to be used by Cloud Run.

#### <ins>Data Source: producer</ins>
A containerized Python script, located in _producer_, that uses a base sample file to generate random fake data records from. It writes parquet files directly to the same GCS bucket the app will read from.

This is deployed as a Cloud Run Job and is currently set to produce around 32,000 records every 2 minutes with a schedule created by Cloud Scheduler (look for _"data-producer-job"_ and _"schedule-producer"_ in _terraform/main.tf_).
The _docker_ directory contains the Dockerfile for building the image to be used by Cloud Run.

#### <ins>Orchestration</ins>
Airflow makes the API requests and loads the results to another bucket in GCS.
There are two DAGs for that: one that makes the request and stores the returned records in a local parquet file, which decouples the task of consuming data from uploading data, and the other that is triggered upon completion of the consuming DAG to perform the uploading.

It makes a request for new data every 5 minutes.
It is (maybe?) easier to use Cloud Composer 2 for deployment, which is Google's managed orchestration service, built on top of Airflow, but it comes as a more expensive alternative. Instead, I decided to go with a Compute Engine instance (look for the _"google_compute_instance"_ resource in _terraform/main.tf_).
This approach requires installing Airflow in the VM, for which I decided to use Docker again.

In the _docker_ directory there's one Dockerfile for Airflow, which is used to extend the base Airflow image by installing the required dependencies. The _compose.yml_ file is similar to the one provided by the official Airflow documentation for getting started with Airflow-Docker, but it's a lightweight version that I used for local development.

If you wish to connect to the Airflow web server once it's up, you just have to connect to the public IP assigned to your Compute Engine VM. It uses a self-signed certificate for SSL so your browser will likely issue a warning about that connection. You can proceed to login using the username and password found in _compose.yml_, look for the line with _AIRFLOW_WWW_USER_USERNAME_. Don't change these values (see next paragraph).

The process of installing both Docker and Airflow in the VM is automated with Terraform: you can run a script upon VM creation. The script is _startup-script.sh_ in the _terraform_ directory, which will download the files from this GitHub repository, including _compose.yml_. This means changing the file locally will not change it in the VM; you would have to modify the startup script.

#### <ins>Data Warehouse</ins>
Naturally, BigQuery is used. Two tables are created: one when _init2-apply.sh_ runs, called _"raw_videogame_table"_, and the other when the dbt Cloud Run job runs (look for the _"raw_data_table"_ resource in _terraform/main.tf_).

The raw table is used just as a means for dbt to be able to access the files in the GCS bucket, so it is created as an external table (it is not loaded into BigQuery therefore no additional storage costs are incurred). It is also partitioned, which means any dbt models can run a SQL WHERE clause to filter out unneeded data and hence reduce query costs.

#### <ins>Transformations</ins>
dbt is containerized and runs as a Cloud Run Job, scheduled with Cloud Scheduler to run every 20 minutes for replication purposes (look for _"dbt-job"_ in _terraform/main.tf_). It is coded to read all data created on the current day, so if you let it run twice it will append every record again plus new records. If there was no need for replication, the job would be scheduled to execute just once at the end of the day, transforming just the new daily data.

The file _dbt/my_zoomcamp_project/entrypoint.sh_ creates an environment variable with the current day, making it accessible by the dbt model (_dbt/my_zoomcamp_project/models/staging/videogame_sales.sql_) to use a WHERE clause.

One nice thing about the model is that it is incremental. This means dbt does not read all the of the data in the raw data table each time the model runs. A SQL WHERE clause can be used to transform only the newly obtained raw data, perform transformations, and then append to another table. This is where the second table, _"videogame_sales"_, is created. Again, this table is partitioned to reduce query costs and increase performance. I did not find any obvious columns to cluster, but suppose you always analyze, let's say, the Publisher column, then you could cluster by it.

One issue that I stumbled upon is that there is no way to create a _UNIQUE constraint_ on any columns without having dbt perform full table scans to check if a given entry for that column is unique or not. I believe this is because BigQuery does not enforce primary keys, so my model ends up just appending every new record of data, even if it were to introduce duplicate rows.

I had originally planned to create more fake data and put those in different endpoints, so I could have multiple tables (fact and dimension tables) in BigQuery to analyze. Since the project deadline is April 15, I am left with very basic transformations in my dbt model.

#### <ins>Customizable code</ins>
In _terraform/main.tf_, there are some blocks of code commented out. For example, if you want to SSH into the VM instance, you can use the *file* Terraform function to point to a key. You can also modify the cron expressions for the dbt and data producer jobs. Or maybe modify _terraform/variables.tf_ to change the region where each resource is deployed. I only tested the default values though.