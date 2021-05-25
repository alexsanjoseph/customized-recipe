# customized-recipe

## Description

This package was created as a part of Course CSE6242

This package contains the code and datasets required 
to run the Customized Recipe Finder. A user can provide
details of their nutritional needs as well as some other
necessary information which enables the system process, 
filter and provide information via vizualization and 
recipe recommendations, to the user. 

## Installation

MINIMUM HARDWARE REQUIREMENTS 
=================================

4GB RAM 
Dual Core

RECOMMENDED HARDWARE REQUIREMENTS 
=================================

8GB RAM 
Quad Core

PREREQUISITIES
=================================

- Python 3.6+
- Docker 1.19+

INSTALLATION 
=================================
1) Install the following packages 
using pip , pip install <package>:

sklearn, plotnine, elasticsearch, 
tqdm, streamlit

2) Make sure docker service is started

## Execution

here are two ways to deploy the App

1) Docker-compose
- Go to the directory where docker-compose.yml is located
- From terminal run 'docker-compose up'
- Wait for "Analysis Ready!!!" message on console (takes roughly two minutes)

OR Alternately, you can run from the source

2) Running from source, with just ES in Docker
- Download the codebase
- Naviage to the root directory
- Run 'docker-compose -f docker-compose_es.yml up'
- On a different terminal, run 'python3 setupCustomizedRecupe.py'
- Run 'streamlit run src/ui2.py'

## Accesing the App
- From a web browser access 0.0.0.0:8501 to use the webapp

## Demo Video

A Demo video can be found here -

## Team

Team 161 A2N2S2

Alex Joseph
Aman Bansal
Nachiket Kulkarni
Nikhil Handa
Surbhi Jain
Swapnil Jha