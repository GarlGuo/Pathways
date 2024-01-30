# Pathways

## Installation

Note: This installation guide assumes familiarity with command line on unix like systems. It is tailored toward macOS,
as most of the developers on this project use macs. Windows and Linux installations will have the same dependecies, although
installations may vary. Contact the lead backend developers with questions / concerns.

Clone the repository in the directory where you would like the application to
live.

```
git clone https://github.coecis.cornell.edu/Pathways/PathwaysApp-Public
```
## Global Installations

Install xmlsec, using brew if on mac (otherwise, google xmlsec install + your machine here)

```
brew install Libxmlsec1
brew install pkg-config
```

If you are unsure whether either of these packages is installed, run the following command to determine whether it has been installed or not.

```
brew install -v package-name
```

## Create Virtual Environment (Done only once)


### <strong> For Unix system users </strong>
Navigate to the ```react-app/api``` folder, and run:

If you don't have pip, run:

```
python get-pip.py
```

If you don't have virtualenv, 


```
python3 -m pip install --user virtualenv
```

Create a new virtual environment:

```
python3 -m venv venv
```

Activate the virtual environment:

```
source venv/bin/activate
```

Install all of these packages, once you have activated
your virtual environment.

```
pip install python-dotenv Flask-PyMongo nltk pandas scikit-learn numpy autocorrect python3-saml onelogin xmlsec argparse guppy3 redis scipy openpyxl
```

At this point, you python environment should be set up. If there are any issues
during the installation process, contact the lead backend developer.

### <strong> For Windows system users </strong>
Navigate to the ```react-app/api``` folder, and run:

If you don't have pip, run:

```
python get-pip.py
```

If you don't have virtualenv, 


```
python -m pip install --user virtualenv
```

Create a new virtual environment, please <strong>click</strong> the <em>create_venv_windows.cmd</em> file


Activate the virtual environment:

```
api\venv\Scripts\activate.bat
```

Install all of these packages, once you have activated
your virtual environment.

```
pip install python-dotenv Flask-PyMongo nltk pandas scikit-learn numpy autocorrect python3-saml onelogin xmlsec argparse guppy3 redis scipy openpyxl
```

At this point, you python environment should be set up. If there are any issues
during the installation process, contact the lead backend developer.


## Install and Set Up Database

This is the first step. Install mongoDB (default for mac is homebrew
installation). If you are not using mac, refer to:
```
https://docs.mongodb.com/manual/installation/
```

```
brew tap mongodb/brew
brew install mongodb-community@4.4
brew install redis
```

Create a new folder from your home directory called ```~/data/db```.

# Run the App

## 1. Launch Database

Navigate to the root folder of the repository and run ```./start_mongo.sh```.
You should see a lot of text come up in the screen, meaning that the database is running.
For testing and development purposes, keep this terminal
window open as long as you want the database to run. If you know tmux, you can
also run the database using a detachable tmux session so you don't have to keep the terminal
window open.

```./clear_mongo.sh``` is a script for removing all of the data from the database, and should only
be used in testing and development setups.

clicks on ```start_redis.cmd``` to start redis server on windows, or run ```./start_redis.sh``` in linux system.

```stop_redis.cmd``` can shutdown redis server on windows and run ```./stop_redis.sh``` on linux system do the same thing.

## 2. Launch Backend

Navigate to ```react-app/api``` and <strong>click</strong> <em>generate_data.cmd</em> file on windows, or run ```./generate_data.sh``` on Mac. This will output
the necessary .pickle files that the backend reads (this only needs to be done once, unless
the csv files have been updated).

Navigate to ```Pathways/react-app``` in a separate terminal session and run
```npm start```. This will start the backend server. If you are getting
dependency not satisfied errors, activate the virtual environment (per above)
and do ```pip install <insert-dependency-here>```.

If you get errors when running ```npm start``` and the errors are not dependency errors, navigate to ```Pathways/api```
in a separate terminal session and run ```flask run```

## 3. Launch Frontend

Navigate to ```Pathways/react-app``` in a separate terminal session and run
```npm start```. This will start the frontend server. If you are getting
dependencny not satisfied errors, do ```npm install insert-dependency-here``` in
```Pathways/react-app``` folder.

## Troubleshooting

Activate the virtual environment (```source venv/bin/activate``` on Mac or ```venv\Scripts\activate.bat``` from ```api```
folder) and do ```pip install insert-dependency-here```.

Dependency not satisfied errors with react: do 
```npm install insert-dependecy-here``` from ```Pathways/react-app``` folder  to
add dependencies not downloaded.

SSL: CERTIFICATE_VERIFY_FAILED error: see answers to this question:
https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org

### For backend issues, please contact Wentao (wg247)
