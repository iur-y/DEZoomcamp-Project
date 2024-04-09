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
### I recommend that you read all the steps below from start to finish before replicating them, so you have an idea of what to expect
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
    * 4.3 Click _**CONTINUE**_ > _**DONE**_
    * 4.4 You should see an email address created for the service account that looks like `name@project.iam.gserviceaccount.com`. Copy it to somewhere as it will be needed later
5. Create a key
    * 5.1 Still in the same service accounts page, you can click on the email and it should redirect you to a page where you can then go to _**KEYS**_ > _**ADD KEY**_ > _**CREATE NEW KEY**_ > _**JSON**_ > _**CREATE**_
    * 5.2 Put the key in the _creds_ directory, which is located in the root of the cloned repository
    * 5.3 Rename the key to **my-creds.json**
6. Replace the project id and service account email
    * 6.1 Edit the _terraform/variables.tf_ file and replace the fields that are commented out, **keep the double quotes but remove the `<` and `>` symbols**
    * 6.2 Uncomment those two lines, it should look like `default = "your_project_id"` and `default = "your_service_account_email"`
7. Run the scripts in order
    * 7.1 `./pre-init.sh`\
    This is meant to get user input to create the Cloud Storage bucket names, since they have to be globally unique
    * 7.2 `./init1-push.sh`\
        This builds the Docker images and pushes them to Artifact Registry where they are kept. It also uses Terraform to enable the required APIs to do that
    * 7.3 Ideally now you wait until the time is 1 minute before a multiple of 20, i.e. **hh:19 or hh:39 or hh:59** and only then run `./init2-apply.sh`\
        This is because the dbt container runs following the **\*/20 \* \* \* \*** cron expression, and it won't be created and ready to run in just 1 minute (detailed information about the code is in a section below). Anyway, what _init2-apply.sh_ does is create all the other resources with the command _**terraform apply**_, such as the Compute Engine, Cloud Run application, BigQuery dataset and table and Cloud Run Jobs. Note that you will have to type _**yes**_ for confirmation
8. Poke around. Now that every resource is created, you can navigate to their respective pages and see what was created:
    * 8.1 Cloud Storage should have two buckets
    * 8.2 BigQuery should have a dataset and a table (two after the dbt job runs)
    * 8.3 Cloud Run should have the application running
    * 8.4 Cloud Run Jobs should have two jobs listed
    * 8.5 Cloud Scheduler should have one schedule for each Cloud Run Job
9. At **hh:00 or hh:20 or hh:40**, the dbt job will start running and create a second table in BigQuery. After the job concludes (check status on the Cloud Run Jobs page), run
    * 9.1 `./terminate1.sh`\
    This will terminate all the major billable resources such as the Compute Engine and Cloud Run service, but it keeps the dataset in BigQuery and the Cloud Storage buckets in case you wish to run queries, inspect the data or use a BI tool to create a dashboard
    * 9.2 `./terminate2.sh`
    This does _**terraform destroy**_ and will also ask for input. Enter _**yes**_ for confirmation. After that, you can delete the Google Project should you prefer

# Code, infrastructure and project details
### Code
I like to comment a lot which means you will find many comments in most files should you want to see how something was done

### Infrastructure
