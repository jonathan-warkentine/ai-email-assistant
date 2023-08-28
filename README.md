# ai-email-assistant
An AI powered email bot for small businesses that integrates with Workiz for client and lead creation, basic job quoting, as well as job scheduling.

## Build in Docker and Push to AWS ECR
To build for X86 on an ARM machine:

```shell
# Create a new builder instance if you haven't already (you must have Docker installed on your machine)
docker buildx create --use --name mybuilder

# If you already have a builder, move on to the next steps below

# Get a fresh authentication token for your local Docker (you must have AWS CLI installed on your machine)
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <your_aws_ecr_url>

# Build and push the multi-architecture image
docker buildx build --platform linux/amd64,linux/arm64 -t <aws_ecr_url>/<project_name>:<tag> --push .
```



## Deploy in an EC2 Instance
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
docker run -d -p 80:80 your-account-id.dkr.ecr.region.amazonaws.com/your-image-name:tag
```

All set!