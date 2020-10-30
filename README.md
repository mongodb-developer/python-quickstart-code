# MongoDB Python Quick Start Code

This repository contains sample code from the MongoDB Python Quick Start series.

There are currently two posts in the series:

* [Basic MongoDB Operations in Python](https://developer.mongodb.com/quickstart/python-quickstart-crud)
* [Getting Started with Aggregation Pipelines in Python](https://developer.mongodb.com/quickstart/python-quickstart-aggregation)

# How To Run It

The source code is all in the [src](./src) directory.
It is written for Python 3.6 and later.

Full instructions on how to set up your Python environment for this code can be found in the first blog post in the series, [Basic MongoDB Operations in Python](https://developer.mongodb.com/quickstart/python-quickstart-crud).

To install the dependencies, create a virtualenv using your favourite tool, such as [venv](https://docs.python.org/3/tutorial/venv.html) or [virtualenv](https://virtualenv.pypa.io/en/stable/), activate it, and then run:

```bash
python3 -m pip install -r requirements.txt
```

You will also want to set the environment variable `MONGODB_URI` to your MongoDB Atlas cluster, either on the command-line, or in a `.env` file.

Once you've installed the dependencies and set `MONGODB_URI` you can run the python scripts directly with something like:

```bash
python3 src/01_crud_operations.py
```

If you have questions or feedback,
please let us know at the [MongoDB Community Forums](https://community.mongodb.com/)!
