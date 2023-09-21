**TIMER SYSTEM - TABLE OF CONTENTS**
- [OVERVIEW](#overview)
  - [General Description](#general-description)
    - [Key System Features](#key-system-features)
  - [System Performance](#system-performance)
  - [Design Assumptions](#design-assumptions)
  - [Scaling Discussion](#scaling-discussion)
- [Quick Start](#quick-start)
  - [Dependencies](#dependencies)
  - [Build](#build)
  - [Run](#run)


# OVERVIEW

## General Description
The timer system enables clients to schedules webhooks using Rest-Api:  
>The user will define how long from now the webhook should be activated.  
>The webhook that will be fired is the url specified concatenated with the timer's id.  

The system is composed of three components (micro-services):
>1. Rest-API Component (timer_api) - Enables the communication between the system's clients and the system db.  
    The component is responsible to save new timer requests to the db and to fetch their status to the client.
>1. Database (timer_db) - Stores all information about the tasks.  
    Based on MySQL, Can handle the task of locking specific rows in the db which enables single access to a record even with multiple consumers.
>1. Schedule Controller (timer_controller) - Searches for the tasks that need to be process now and launches them.

### Key System Features

>1. **Resilience**
>    * The timer_api and timer_controller try to recover after DB connection failure.  
 The recover properties can be configured using environment variables as specified in the components READ ME files.
>    * After db or controller failure, all missed task are invoked.
>1. **Scalable**
>    * The timer_api and timer_controller are containerized and multiple instances could be added without interfering.
>1. **Accuracy**
>    * The timer_controller checks for tasks to be invoked every 500ms. That value can be configured in order to invoke the webhooks more accurately.


## System Performance
The system performance should be measured using the following metrics:
>1. **Accuracy**: The difference in time webhook was launched vs it's scheduled time.  
>   The wait time between task pulling in the controller can be configured and change the system accuracy.
>1. **Throughput**: The number of simultaneous rest-api requests can be handled and the number of simultaneous tasks that can be fired at the same time.  
    The number of instances of the timer_api and the timer_controller will control the throughput.
>4. **Max Timers Capacity**: The number of waiting tasks can be stored in the db.  
    The size of the db storage will define that metric.

## Design Assumptions
During the design and implementation of the project, some assumption were made.
>1. Each task that was received by the system is considered critical and cannot be missed or invoked more than once. Even if the system crashes. With the expense of delays and rejecting tasks when the service is too busy.
>1. The MySQL component is durable, robust and can handle concurrent client in a safe way. For full horizontal scaling options one should refer the _Scaling Discussion_ section.
>1. The load balance function for the Rest-API is handled by the hosting cloud service (AWS, GCP, OCP, etc)
>1. Difference of up to 1 second between the schedule and actual time is acceptable. As mentioned, the accuracy could be changed easily by changing some configuration values in the controller. However, that will affect the throughput.


## Scaling Discussion
With the following design, the single instance of sql server is a bottle neck. The frequent reads the controllers execute cause freeze in the INSERT operations.
The following aspects can be explored in order to create fully horizontal scalable service or better use of the current design:
>1. Research how to override locks with INSERT in MySQL.
>1. Benchmark different SQL servers for the specific design (faster read/write).
>2. Research MySQL Cluster CGE and how synced is it's locking mechanism in the different node.
>3. Question the requirement to get timer's status.  
 If it's not necessary, multiple independent MySQL instances can be used (see **Horizontal Scaling** tab in the **system_scheme.drawio**).
>4. Reducing the accuracy requirements could allow the controllers to collect messages less frequently.

# Quick Start
## Dependencies
The host machine has to have docker engine installed.  

## Build
1. Pull the mysql:latest image.  
```bash
docker pull mysql:latest
```
2. Use the git submodules to build the api and controller images.  
    >There are two options to build the images for the api and controller: 
    >   1. For OS that support bash script, it is recommended to use it.  
    >   1. For OS that doen't support bash script, use the manual further in the document.
    ### Automated Build
    Use terminal and navigate to the main folder of the project and run the following command.
    ```
    bash .cicd/.cicd.sh
    ```
    The command will build two images from the Dockerfile in the submodules of the project.

    ### Manual Build
   1. Build the api image:
        ```bash
        cd ./timer_api
        docker build --tag timer_api:0.0.1 .
        ```
   2. Build the controller image:
        ```bash
        cd ./timer_controller
        docker build --tag timer_controller:0.0.1 .
        ```

## Run
1. Make sure the compose file is updated with the built images tags:
   ```yaml
    services:
        timer-api:
            image: timer_api:0.0.1 # <<<<<< UPDATE TAG
            container_name: timer_api_1
            networks:
    ...
        timer-controller:
            image: timer_controller:0.0.1 # <<<<<< UPDATE TAG
            container_name: timer_controller_1
            networks:
    ...
   ```
2. Create a folder for the db in the host computer and bind it to the timer_db in the compose file.
    ```bash
    # Example Location
    mkdir /tmp/timer_db
    ```
    ```yaml
        timer-db:
            image: mysql:latest
            container_name: timer_db
            volumes:
                - {host_location}:/var/lib/mysql
                - /tmp/timer_db:/var/lib/mysql # <<<< Example
    ```
    > For non persistance testing the volume bind could be commented in the compose file
3. Run the entire components using the compose up command:
    ```bash
    docker compose up -d
    ```
4. Interact with the timer_api's [swagger interface](http://localhost/docs).

5. Inspect the timer_controller logs:
   ```bash
   docker logs timer_controller_1 -f
   ```