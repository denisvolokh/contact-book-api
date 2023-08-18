# Project Requirements

## 1. Database Setup

- Objective: Set up a Postgres database.
- Tasks:
    - Craete a Postgres database
    - Download the Nimble Contacts in the .csv format
    - Import data from the Nimble Contacts.csv file into your database

## 2. Data Update Logic

- Objective: Implement a mechanism to periodically update the contacts in your database
- Tasks:
    - The contacts should be updated periodically, for instance, once a day.
    - Use technologies like cron, celery, or any other tool you are familiar with to achieve this.
    - The source of the data will be Nimble API, for fetching the contacts, use the following endpoint:
        - Method: GET
        - URL: `https://api.nimble.com/api/v1/contacts`
        - Authentication: Use the Authorization header with your API key
        - Header Example: `Authorization: Bearer YOUR_API_KEY`
    - [Documentation Reference](https://nimble.readthedocs.io/en/latest/contacts/basic/list/)

## 3. Search API

- Objective: Implement an API endpoint that supports full-text search
- Tasks:
    - The API should have a single method that accepts a text string as input
    - Using the given text string, perform a full-text search on the contacts in your database
    - For this, refer to the PostgreSQL documentation on [text search](https://www.postgresql.org/docs/current/textsearch.html)
    - It's preferable not to use an ORM for this task
    - The API should return a list of matching contacts

## 4. Additional Tasks

- Write tests to verify the functionality of your implementations.
- Provide documentation that describes how your solution works.
- Present your work in the form of a GitHub repository.


