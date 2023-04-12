# BallotChain: Blockchain based online voting system - Backend

This is the backend for a project developed using Django that allows users to vote in an online election using blockchain technology. The system is secure, transparent, and tamper-proof. 


## Getting Started

To get started with this project, you need to clone this repository to your local machine and follow the instructions in the [Installing](#installing) section. 

### Prerequisites

To run this project, you need to have the following software installed on your machine:

- Python (v3.8 or higher)
- Django (v3.2 or higher)
- Django REST Framework (v3.12 or higher)

### Installing

### Clone this repository to your local machine

  ```git clone https://github.com/<username>/blockchain-based-online-voting-system-backend.git```

### Create a virtual environment and activate it

    python -m venv venv
    source venv/bin/activate (Linux/MacOS)
    


### Install the dependencies using pip

  pip install -r requirements.txt

### Run database migrations

    python manage.py makemigrations
    python manage.py migrate

### Start the development server

    python manage.py runserver
