# UOCIS322 - Project 7 #
Brevet time calculator with AJAX, MongoDB, RESTful API, and authentication.

## Overview
Brevet control opening and closing time calculator.

This calculator calculates its times based on the RUSA ACP controle time calculator.
For more information: https://rusa.org/pages/acp-brevet-control-times-calculator

## Instructions
For a given brevet distance, the user must input values that correspond to the control distances (in either miles or kilometers) for the given brevet. 
The opening and closing time for each control point will then be calculated.

The control distances MUST:
* Be listed in ascending order.
* Have the last distance be at least the total brevet distance.
* Have all distances be less than 20% longer than the total brevet distance.

The times can now be submitted using the submit button. Once the button has been clicked, all current times will be stored in a database. The display button next to the submit button will then display the last submitted times to the user. 

To submit your times, all warnings must be dealt with beforehand. The submission will not complete unless there are no warnings with the checkpoint times. 

## RESTful API
The project now contains a RESTful API and a consumer program (in the website directory) to utilize it. After submission of a list of brevet checkpoints, the checkpoints can now be viewed with specified parameters (formatting, number of results, etc.). 

## Authentication
To use the provided consumer program, you now need to register an account and login. 
Once the user is logged in, they will be provided a token that will expire after a given period of time. This token is required to access any of the data implemented in the consumer program. 
If the user attempts to access any data without a token, or if the user attempts to access with an expired token, they will be responded with a 401 error and will be asked to log back in.

## Author: Jordan Smith, jsmith37@uoregon.edu ##