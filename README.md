# Pyfiddle

PyFiddle is a free lightweight PYTHON IDE to run and share Python scripts with some nifty features.

 - Running, Saving and Sharing Fiddles for free
 - Pip installation of Packages
 - Arguments to scripts
 - Program inputs to scripts
 - File uploads

# New Features!
 - Minor UI Improvements
 - Option to switch off notifications
 - API endpoint at pyfiddle.io/api/

You can also:
  - Share your fiddles with the world
  - Collaborate on the same fiddle with others
  - Save and Bookmark other fiddles for future reference
  - Make fiddle private


### Tech

Pyfiddle uses open source technologies and AWS services for its infrastructure

* [Django] - Powers the web app!
* [jQuery] - For front end UI functionality 
* [zappa](https://www.zappa.io/) - Acts a Serveless framework which provides an itnerface to AWS CloudFormation.
* [Semantic UI](https://semantic-ui.com) - UI CSS Library
* AWS Lambda (Python Environments) for a Serverless web application
* AWS Lambda (Python Environments) for isolated fiddle executions
* AWS API Gateway for domain endpoints
* AWS RDS (Aurora - MySQL) for storing data
* AWS Cloud Watch for monotioring and logging
* AWS Work Email for email related tasks
* AWS Route 53 for managing domain and DNS


### Plugins

Pyfiddle is currently extended with the following plugins.

| Plugin |
| ------ |
| CodeMirror |
| Google Analytics |
| Session Stack |

### Running
Pyfiddle is designed to run on AWS Lambda.
Deployments are done using Zappa, the serverless framework for Django and AWS.

1. Rename the zappa_settings_example.json to zappa_settings.json
2. Edit the fields with {{}} with your AWS infra values
3. Hit `zappa deploy <StageName>
4. For v2.7 code executions, deploy `pyfiddle_executer` to AWS Lambda as a Python function
5. For v3.6 code executions, deploy `pyfiddle_executer_36` to AWS Lambda as a Python function
6. Voila your app is up and running

Feel free to create multiple stages.

### Todos
 - Fancier UI with more options
 - Interactive Shell
- Subscription model
 - Write MORE Tests

License
----

MIT


**Free Software, Hell Yeah!**

