## A simple flask server secured with Azure B2C Auth
This simple flask server allows for setting up an HTTP server
and authenticating/authorizing users after they sign in with Azure b2c. 

The motivation behind this is to have a simple web interface for IoT projects. 


## Usage/Installation

### Adding admins/users
Users can be added using the command line. The app
implements a simple hasing for emails of the users that are 
simply stored in local text files. See the `./hash_check.py` utility module for more info.
```shell
# adding an admin user:
./hash_check admin_hashed_email_list.txt WRITE admin@email.com

# checking if an email corresponds to entries in the list:
./hash_check admin_hashed_email_list.txt CHECK admin@email.com
```


### Logging in
TODO

## Architecture and Back-end administration

The server is implemented as a reverse-proxy (using `nginx` - which is also used for SSL termination) 
which forward the main endpoint to a Gunicorn implementing the "Web Server Common Interface" to a 
minimal Flask-based app. 

### Authentication
Azure AD B2C is used for authentication. The files follow the tutorial from microsoft for implementing Azure AD B2C.

In order to implement also local "roles" and "rules" a simple hash/salted list of emails is kept.
All endpoints apart from the initial sign-in page are only accessible after Azure AD B2C authenticates that the user is allowed to enter. 
In addition the `hash_check` module checks if the emails are authorized to access particular parts of the app (see also above for how users are added from the server-side).

## TODO:
Make a simple interface to add users (open to "admin users" only that can only be added using an admin-role).

