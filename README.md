# Nanny Kid Playdate

<img width="1469" alt="Screenshot 2023-08-15 at 12 19 43 AM" src="https://github.com/raissaglaucie/nanny-kid-playdate-backend/assets/107502468/51952bcf-2c80-44dd-b8e6-bcc95df549aa">

------------------------------------------------------------------------------------------------------


The Nanny Kid Playdate is a web application that facilitates connecting and arranging playdates for nannies. The application allows users to create profiles, search for other users, follow and unfollow other nannies, post pictures with descriptions about the visited place, and comment on other users' profiles. Users can manage their profiles by providing essential information about themselves and their nanny kids. The project focuses on creating a user-friendly and personalized platform to enhance the playdate experience for nannies and promote social interaction among children.

# Installation-Usage

This project's user interface is constructed using React, a JavaScript library designed to streamline the development of efficient and reusable front-end components. Complemented by Chakra UI, the project leverages features and a virtual Document Object Model (DOM) to optimize the updating and rendering of user interface elements. This optimization leads to an enhanced and seamless user interaction.

Follow these steps to set up both the backend and frontend repositories for the project in a dedicated folder named "nanny-kid-playdate":

1 - Create a new directory to accommodate the backend and frontend repositories: make a directory named "nanny-kid-playdate."

2 - Move into the newly created project folder: go to the "nanny-kid-playdate" directory using the command line.

3 - Clone the frontend repository by copying its content from: https://github.com/raissaglaucie/nanny-kid-playdate-frontend.

4 - Install the necessary dependencies using npm: execute the command "npm install" to acquire the required packages.

5 - Initiate the development server: launch the server for development purposes using the command "npm start."

6 - Access the locally hosted web application: open your web browser and enter the address http://127.0.0.1:8000/ to interact with the web application on your local machine.


# Architecture Diagram

The Architecture Diagram provides an overview of how our application's different components and modules interact. This visual representation helps understand the flow of data and communication within the system.

![FlowChart Nanny kid drawio](https://github.com/raissaglaucie/nanny-kid-playdate-backend/assets/107502468/9b61e9bf-afe7-4e39-ac0a-ce124ab9e294)


Frontend: This is where the user interface is built using React and Chakra UI. It communicates with the backend to fetch and display data.

Backend: The backend, built using Django, handles the business logic and interacts with the database to store and retrieve data.

Database: PostgreSQL, our chosen database system, stores all the necessary data for the application. It's accessed by the backend for data manipulation.

API Communication: The front end and back end communicate via RESTful APIs. This allows them to exchange data and requests seamlessly.

User Authentication: I am using Token-based Authentication to manage user authentication and ensure secure access to the application.


# Interaction Flow:

1 - A user interacts with the web application through the front-end user interface.

2 - The front end requests the backend API to fetch or manipulate data.

3 - The backend processes these requests, interacts with the database if needed, and sends back the appropriate response to the front end.

4 - User authentication and authorization are managed by Token-based Authentication, ensuring secure access to the application's features.

5 - Data retrieved from the database is presented to the user through the front end's UI.

# Accessing the Deployed Version

You can access the deployed version of Nanny Kid Playdate application by following the link below:

[Deployed version](https://nanny-kid-playdate-frontend.vercel.app/).

Click on the link above or copy-paste it into your web browser's address bar to open the application. This version of the application is hosted and accessible online, allowing you to explore its features and functionality without needing to set up anything locally.

Please note that this deployed version is always available and provides a convenient way to experience the application without any additional setup.

Feel free to provide feedback, report issues, or share your thoughts on the application.


