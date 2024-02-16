# Repository & Virtual Environment Setup

## Contributing
If you are contributing to this project, please follow these steps:

You can:
1. Fork the repository: <br />
To fork this project, click the "Fork" button in the top-right corner of the GitHub page or [click here](https://github.com/cjunwon/SRILab-Parked-Cars-Road-Classification).

Configure this remote repository for a fork (set upstream). Documentation can be found [here](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/configuring-a-remote-repository-for-a-fork).

2. Clone the forked repository onto your device.

> You can work on the ```main``` branch on your forked repo and then create a pull request.

OR you can:

1. Clone the repository directly.
2. Create a new branch:
```
git checkout -b my-new-branch
```
---

3. Navigate to the project directory (where you cloned the repository)

```
cd HSPA-Update-Pipeline
```

4. Install pipenv:

```
pip install pipenv
```

5. Sync required packages:
```
pipenv sync
```
> This should install all required packages in the repo.

6. Activate the virtual environment:
```
pipenv shell
```

> **Note for contributers (SRILab Team members):** <br />
Make sure to run **'pipenv lock'** after you **'pipenv install'** any new packages.

7. Make your changes and commit them:
```
git commit -m 'Add new feature'
```
8. Push your changes to your fork:
```
git push origin my-new-feature
```
9. Create a pull request.

> **Note for contributers (SRILab Team members):** <br />
If you are working with an **ipynb** file, make sure the kernal is set to the project's pipenv.


---

# Amazon S3 & Boto3 Notes
## AWS CLI

*Install AWS CLI:* [[Link]](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

### Setup Boto3 User credentials

#### Create Boto3 User
- Head to IAM Dashboard
- Go to Users
- Add users (User name: ```Boto3-User```)
- From Permissions Options, choose "Attach policies directly"
- From Permissions Policies, checkoff "Administrator Access"
- (Skip tags)

#### Retrieve User Access keys
- Go to newly created Boto3-User page
- Under Summary, create Access Key
- Use case: Local code (Running Boto3 off local pipeline)
- Retrieve and store securely: Access Key ID, Secret Access Key
  - To securely store your keys, create a new file in the repository and name it ```config.py```, which can be structured in the following way:
```python
ACCESS_KEY = 'abcdefg123'
SECRET_ACCESS_KEY = 'hijklmn456'
```
  The ```.gitignore``` file should ignore this file when committing to GitHub, and you should keep this file only on your local device.

#### Configure and login to IAM User (on local machine)
>```aws configure```         Creates a [default] profile
- Type the above into local CLI environment (e.g. Terminal)
- Enter in Access Key credentials
- Default region name: us-east-1    *(doesn't matter too much)*

Reference materials for Boto3 Python library stuff:
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-examples.html
