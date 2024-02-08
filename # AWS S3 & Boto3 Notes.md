# AWS S3 & Boto3 Notes
## AWS CLI

*Install AWS CLI:* [[Link]](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

### Environment setup
To install the necessary dependencies (*alternatively use pip3*):
>`pip install -r requirements. txt`

### Setup Boto3 User credentials

#### Create Boto3 User
- Head to IAM Dashboard
- Go to Users
- Add users (User name: Boto3-User)
- From Permissions Options, choose "Attach policies directly"
- From Permissions Policies, checkoff "Administrator Access"
- (Skip tags)

#### Retrieve User Access keys
- Go to newly created Boto3-User page
- Under Summary, create Access Key
- Use case: Local code (Running Boto3 off local pipeline)
- Retrieve and store securely: Access Key ID, Secret Access Key

#### Configure and login to IAM User (on local machine)
>`aws configure`         Creates a [default] profile
- Type the above into local CLI environment (e.g. Terminal)
- Enter in Access Key credentials
- Default region name: us-east-1    *(doesn't matter too much)*
