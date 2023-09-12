# ai-email-assistant
An AI powered email bot for small businesses that integrates with Workiz for client and lead creation, basic job quoting, as well as job scheduling.

## Setup
1. After setting up a service account with API access to your Workspace's Gmail, obtain the `service account key` for this account and save the contents in a `config/credentials.yaml` file. The values should be nested under `gmail.credentials` (more info in the README within `configs` dir).
2. Obtain your API key for Workiz and save it in the same `config/credentials.yaml` file, under `workiz.credentials`.
3. In `config/config.yaml`, set the appropriate  of the account in your workspace for which this AI bot will be generating emails.

## Running Locally
From the root:
```shell
pip install -r requirements.txt
python main.py
```

## Deploy

### Build in Docker and Push to AWS ECR

To build for X86 on an ARM machine:

```shell
# Create a new builder instance if you haven't already (you must have Docker installed on your machine)
docker buildx create --use --name <your-builder-name>

# Or if you already have a builder:
docker buildx use <your-builder-name> 

# Get a fresh authentication token for your local Docker (you must have AWS CLI installed on your machine)
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <your_aws_ecr_url>

# Build and push the multi-architecture image
docker buildx build --platform linux/amd64,linux/arm64 -t <aws_ecr_url>/<project_name>:<tag> --push .
```



### Deploy in an EC2 Instance
1. Create your EC2 instance. SSH into that instance.
2. Install and start Docker, ensure that it starts on boot:
```shell
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo systemctl enable docker
```
3. Install and configure AWS CLI:
```shell
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
sudo aws configure
```
4. To avoid getting permission denied errors:
```shell
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world
```
5. Authenticate Docker with AWS:
```shell
aws ecr get-login-password --region region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.region.amazonaws.com
```
6. Pull your ECR image:
```shell
docker pull your-account-id.dkr.ecr.region.amazonaws.com/your-image-name:tag
```
7. Run your Docker image:
```shell
docker run -d your-account-id.dkr.ecr.region.amazonaws.com/your-image-name:tag
```

All set!