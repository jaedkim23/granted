# Localizing the HERD Database

**Organizations:** University of San Diego, Elon University, Pepperdine University

**Project Funded by:** NSF

---

## 📖 Overview

This is a repository for the GRANTED project specifically for working with the NSF HERD data. The figure below shows the main steps of the project. The main scripts create the backend database structure and maps the relevant fields to the correct tables in the database. Any application can connect to the database. There is an example Tableau application provided in the repo. 

![Process Overview](<Assets/Process Overview.png>)

There are two main ways to replicate the project for your own organzation. 

---

## Method 1 - Use Existing Web Infrastructure

The first method involves integrating the application directly into your organization's existing web infrastructure. For example, the University of San Diego (USD) created a Tableau application that directly displays on its webpage (see below).

![option1](<Assets/option1.png>)

In this case, it's most likely that your organization's IT department would have to provide support in integration your application directly into the existing websites. Here is a step-by-step guide to creating your own HERD reporting application.

* **Step 1: Create the Database Schema**
Use the file "create_herd_tbl_maria.sql" to create the database schema. The ER diagram of the database schema is shown below.

![ER_Diagram](<Assets/ER_Diagram.png>)

This database will organize information from the following tables from the NSF HERD website (as of 2024 release).

1) Table 13 - Higher education R&D expenditures at institutions in the standard form survey population, ranked by FY 2024 R&D expenditures: FYs 2010–24
2) Table 14 - Higher education R&D expenditures at institutions in the standard form survey population, ranked by all R&D expenditures, by source of funds: FY 2024
3) Table 15 - Higher education R&D expenditures at institutions in the standard form survey population, ranked by all R&D expenditures, by R&D field: FY 2024
4) Table 27 - Headcount and FTEs of R&D personnel at higher education institutions in the standard form survey population, by state, institutional control, institution, and personnel function: FY 2024

Remember to create an environment file that stores all relevant credentials like the server address, port number, username, and password. 

We now add the corresponding records into the relevant tables created in step 1.

* **Step 2: Extract, Transform and Load Data**
Use the files "HERD_download_maria_aws.py" and "HERD_functions.py" to map the data from the NSF HERD website into the database created in step 1. Both files are Python scripts and automatically maps the correct data fields into the correct fields/tables. You only have to run the "HERD_download_maria_aws.py" file to add the records into the tables (this file uses the functions in "HERD_functions.py"). 

Note: The Python scripts require access to the local environment (.env) file with credentials to the database created in step 1. 

Once the "HERD_download_maria_aws.py" script terminates, the relevant data from the 4 tables from NSF HERD are now available for your use. You can create your own application using the database or use the Tableau example in the next step.

* **Step 3: Data Visualization (Tableau)**
You can use the following PDF file for a step-by-step instructions on how to connect your DB to Tableau to create your own application.

        [MariaDB Tableau Integration](<Assets/MariaDB Tableau Integration.pdf>)


* **Step 4: Integrate into Existing Webpages**
You can insert your Tableau application as an iframe element directly into your existing webpages. It is strongly recommended to consult your organization's IT or web team for this step.



## Method 2 - "Turnkey" 

The second method is similar to Method 1 but it is for organizations without existing web resources for direct integration. In this method, there is no chanage in step 1, 2, and 3. The only difference is in step 4 since there is no existing webpages to integrate the Tableau applications. 

![Process_Steps](<Assets/Process_Steps.png>)

Refer to Steps 1, 2, and 3 prescribed in Method 1. 

* **Step 4: Create Web Resources**
TBD
