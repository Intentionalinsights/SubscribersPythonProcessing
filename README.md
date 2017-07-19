# Process Representatives standalone Python tool

This tool processes a csv in the file format exported out of www.protruthpledge.com

It summarizes the amount of users in a given region and lists the representatives at the state level for each region.
The Google Civic API is the primary driver of the information retrieved: https://developers.google.com/civic-information/docs/v2/representatives/representativeInfoByAddress

#Setup

Utilizes python 2.7.x

#IDE recommended for mac https://www.jetbrains.com/pycharm/

Main entry point for runtime configuration: ProcessRepresentatives.py

##Libraries used

    pip install requests

##Data files setup

Make sure you create a data/ folder at the root of the project. Subscriber data is read from this folder but is in
.gitignore file to avoid people accidentally submitting list of users to repo.

##Requires a Google API key

You will need to create a project and then create credentials:

https://console.developers.google.com/apis/credentials

Make an environment variable 'GOOGLE_KEY' and store the key within there.

You will also need to enable the Google API + usage via for this specific Civic service API:

    https://console.developers.google.com/apis/api/civicinfo.googleapis.com/overview?project=<YOUR_PROJECT_NAME>

#Further help

    contact juan_moreno@juansolutions.com
