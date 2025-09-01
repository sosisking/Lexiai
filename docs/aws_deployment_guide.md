# LexiAI AWS Deployment Guide

This guide provides step-by-step instructions for deploying the LexiAI application to Amazon Web Services (AWS).

## Prerequisites

Before you begin, make sure you have:

1. An AWS account with appropriate permissions
2. AWS CLI installed and configured
3. Docker and Docker Compose installed locally
4. The LexiAI codebase

## Architecture Overview

The deployment architecture consists of:

- **Amazon EC2**: For hosting the application containers
- **Amazon RDS**: For PostgreSQL database
- **Amazon ElastiCache**: For Redis cache
- **Amazon S3**: For document storage
- **Amazon CloudFront**: For content delivery (optional)
- **Amazon Route 53**: For DNS management (optional)
- **AWS Certificate Manager**: For SSL certificates (optional)

## Step 1: Set Up the VPC and Network

1. Create a new VPC:

```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=LexiAI-VPC}]'
```

2. Create public and private subnets:

```bash
# Create public subnets
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=LexiAI-Public-1a}]'
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=LexiAI-Public-1b}]'

# Create private subnets
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.3.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=LexiAI-Private-1a}]'
aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.4.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=LexiAI-Private-1b}]'
```

3. Create an Internet Gateway and attach it to the VPC:

```bash
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=LexiAI-IGW}]'
aws ec2 attach-internet-gateway --internet-gateway-id <igw-id> --vpc-id <vpc-id>
```

4. Create a route table for public subnets:

```bash
aws ec2 create-route-table --vpc-id <vpc-id> --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=LexiAI-Public-RT}]'
aws ec2 create-route --route-table-id <public-rt-id> --destination-cidr-block 0.0.0.0/0 --gateway-id <igw-id>
aws ec2 associate-route-table --route-table-id <public-rt-id> --subnet-id <public-subnet-1a-id>
aws ec2 associate-route-table --route-table-id <public-rt-id> --subnet-id <public-subnet-1b-id>
```

5. Create a NAT Gateway for private subnets:

```bash
aws ec2 allocate-address --domain vpc
aws ec2 create-nat-gateway --subnet-id <public-subnet-1a-id> --allocation-id <eip-allocation-id> --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=LexiAI-NAT}]'
```

6. Create a route table for private subnets:

```bash
aws ec2 create-route-table --vpc-id <vpc-id> --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=LexiAI-Private-RT}]'
aws ec2 create-route --route-table-id <private-rt-id> --destination-cidr-block 0.0.0.0/0 --nat-gateway-id <nat-gateway-id>
aws ec2 associate-route-table --route-table-id <private-rt-id> --subnet-id <private-subnet-1a-id>
aws ec2 associate-route-table --route-table-id <private-rt-id> --subnet-id <private-subnet-1b-id>
```

## Step 2: Set Up the Database (RDS)

1. Create a security group for the database:

```bash
aws ec2 create-security-group --group-name LexiAI-DB-SG --description "Security group for LexiAI database" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <db-sg-id> --protocol tcp --port 5432 --source-group <app-sg-id>
```

2. Create a subnet group for RDS:

```bash
aws rds create-db-subnet-group --db-subnet-group-name lexiai-db-subnet-group --db-subnet-group-description "Subnet group for LexiAI database" --subnet-ids "<private-subnet-1a-id>" "<private-subnet-1b-id>"
```

3. Create the PostgreSQL database:

```bash
aws rds create-db-instance \
  --db-instance-identifier lexiai-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 15.3 \
  --master-username lexiai \
  --master-user-password <password> \
  --allocated-storage 20 \
  --db-subnet-group-name lexiai-db-subnet-group \
  --vpc-security-group-ids <db-sg-id> \
  --db-name lexiai \
  --backup-retention-period 7 \
  --multi-az \
  --storage-type gp2 \
  --no-publicly-accessible
```

## Step 3: Set Up ElastiCache for Redis

1. Create a security group for Redis:

```bash
aws ec2 create-security-group --group-name LexiAI-Redis-SG --description "Security group for LexiAI Redis" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <redis-sg-id> --protocol tcp --port 6379 --source-group <app-sg-id>
```

2. Create a subnet group for ElastiCache:

```bash
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name lexiai-redis-subnet-group \
  --cache-subnet-group-description "Subnet group for LexiAI Redis" \
  --subnet-ids "<private-subnet-1a-id>" "<private-subnet-1b-id>"
```

3. Create the Redis cluster:

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id lexiai-redis \
  --engine redis \
  --cache-node-type cache.t3.small \
  --num-cache-nodes 1 \
  --cache-subnet-group-name lexiai-redis-subnet-group \
  --security-group-ids <redis-sg-id>
```

## Step 4: Set Up S3 for Document Storage

1. Create an S3 bucket:

```bash
aws s3api create-bucket --bucket lexiai-documents --region us-east-1
```

2. Configure bucket policy for private access:

```bash
aws s3api put-bucket-policy --bucket lexiai-documents --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::lexiai-documents",
        "arn:aws:s3:::lexiai-documents/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}'
```

3. Enable server-side encryption:

```bash
aws s3api put-bucket-encryption --bucket lexiai-documents --server-side-encryption-configuration '{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }
  ]
}'
```

## Step 5: Set Up EC2 for Application Hosting

1. Create a security group for the application:

```bash
aws ec2 create-security-group --group-name LexiAI-App-SG --description "Security group for LexiAI application" --vpc-id <vpc-id>
aws ec2 authorize-security-group-ingress --group-id <app-sg-id> --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id <app-sg-id> --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id <app-sg-id> --protocol tcp --port 22 --cidr <your-ip>/32
```

2. Create an IAM role for EC2 with S3 access:

```bash
aws iam create-role --role-name LexiAI-EC2-Role --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

aws iam attach-role-policy --role-name LexiAI-EC2-Role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam create-instance-profile --instance-profile-name LexiAI-EC2-Profile
aws iam add-role-to-instance-profile --role-name LexiAI-EC2-Role --instance-profile-name LexiAI-EC2-Profile
```

3. Launch an EC2 instance:

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name <your-key-pair> \
  --subnet-id <public-subnet-1a-id> \
  --security-group-ids <app-sg-id> \
  --iam-instance-profile Name=LexiAI-EC2-Profile \
  --user-data file://ec2-user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=LexiAI-App}]' \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":30,"VolumeType":"gp2"}}]'
```

4. Create a file named `ec2-user-data.sh` with the following content:

```bash
#!/bin/bash
yum update -y
yum install -y docker git
systemctl start docker
systemctl enable docker
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Clone the repository
git clone https://github.com/yourusername/lexiai.git /opt/lexiai
cd /opt/lexiai

# Create environment file
cat > .env << EOL
FLASK_ENV=production
PORT=80
POSTGRES_USER=lexiai
POSTGRES_PASSWORD=<db-password>
POSTGRES_DB=lexiai
DATABASE_URL=postgresql://lexiai:<db-password>@<rds-endpoint>:5432/lexiai
REDIS_URL=redis://<redis-endpoint>:6379/0
SECRET_KEY=<secret-key>
JWT_SECRET_KEY=<jwt-secret-key>
STRIPE_SECRET_KEY=<stripe-secret-key>
STRIPE_PUBLISHABLE_KEY=<stripe-publishable-key>
STRIPE_WEBHOOK_SECRET=<stripe-webhook-secret>
OPENAI_API_KEY=<openai-api-key>
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=<aws-access-key>
AWS_SECRET_ACCESS_KEY=<aws-secret-key>
AWS_S3_BUCKET=lexiai-documents
AWS_REGION=us-east-1
EOL

# Build and start the application
docker-compose build
docker-compose up -d

# Initialize the database
docker-compose exec -T backend flask db init
docker-compose exec -T backend flask db migrate -m "Initial migration"
docker-compose exec -T backend flask db upgrade
```

## Step 6: Set Up SSL with AWS Certificate Manager (Optional)

1. Request a certificate:

```bash
aws acm request-certificate \
  --domain-name lexiai.yourdomain.com \
  --validation-method DNS \
  --subject-alternative-names www.lexiai.yourdomain.com
```

2. Create DNS records for validation (follow the instructions in the AWS console).

## Step 7: Set Up Route 53 for DNS (Optional)

1. Create a hosted zone (if you don't have one already):

```bash
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)
```

2. Create an A record pointing to your EC2 instance:

```bash
aws route53 change-resource-record-sets --hosted-zone-id <hosted-zone-id> --change-batch '{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "lexiai.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "<ec2-public-ip>"
          }
        ]
      }
    }
  ]
}'
```

## Step 8: Set Up CloudFront for Content Delivery (Optional)

1. Create a CloudFront distribution:

```bash
aws cloudfront create-distribution \
  --origin-domain-name lexiai.yourdomain.com \
  --default-root-object index.html \
  --aliases lexiai.yourdomain.com www.lexiai.yourdomain.com \
  --ssl-support-method sni-only \
  --acm-certificate-arn <certificate-arn>
```

## Step 9: Configure Monitoring and Logging

1. Set up CloudWatch for monitoring:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name LexiAI-CPU-Alarm \
  --alarm-description "Alarm when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceId,Value=<instance-id> \
  --evaluation-periods 2 \
  --alarm-actions <sns-topic-arn>
```

2. Set up CloudWatch Logs for log aggregation:

```bash
aws logs create-log-group --log-group-name /lexiai/application
```

## Step 10: Set Up Auto Scaling (Optional)

1. Create a launch template:

```bash
aws ec2 create-launch-template \
  --launch-template-name LexiAI-Launch-Template \
  --version-description "Initial version" \
  --launch-template-data '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "t3.medium",
    "KeyName": "<your-key-pair>",
    "SecurityGroupIds": ["<app-sg-id>"],
    "IamInstanceProfile": {
      "Name": "LexiAI-EC2-Profile"
    },
    "UserData": "<base64-encoded-user-data>",
    "BlockDeviceMappings": [
      {
        "DeviceName": "/dev/sda1",
        "Ebs": {
          "VolumeSize": 30,
          "VolumeType": "gp2"
        }
      }
    ],
    "TagSpecifications": [
      {
        "ResourceType": "instance",
        "Tags": [
          {
            "Key": "Name",
            "Value": "LexiAI-App"
          }
        ]
      }
    ]
  }'
```

2. Create an Auto Scaling group:

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name LexiAI-ASG \
  --launch-template LaunchTemplateName=LexiAI-Launch-Template,Version='$Latest' \
  --min-size 1 \
  --max-size 3 \
  --desired-capacity 1 \
  --vpc-zone-identifier "<public-subnet-1a-id>,<public-subnet-1b-id>" \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --tags Key=Name,Value=LexiAI-App,PropagateAtLaunch=true
```

## Step 11: Set Up Load Balancing (Optional)

1. Create a target group:

```bash
aws elbv2 create-target-group \
  --name LexiAI-TG \
  --protocol HTTP \
  --port 80 \
  --vpc-id <vpc-id> \
  --health-check-protocol HTTP \
  --health-check-path /api/v1/health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2
```

2. Create a load balancer:

```bash
aws elbv2 create-load-balancer \
  --name LexiAI-ALB \
  --subnets <public-subnet-1a-id> <public-subnet-1b-id> \
  --security-groups <app-sg-id> \
  --scheme internet-facing \
  --type application
```

3. Create a listener:

```bash
aws elbv2 create-listener \
  --load-balancer-arn <load-balancer-arn> \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

4. Add HTTPS listener (if using SSL):

```bash
aws elbv2 create-listener \
  --load-balancer-arn <load-balancer-arn> \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=<certificate-arn> \
  --default-actions Type=forward,TargetGroupArn=<target-group-arn>
```

5. Update the Auto Scaling group to use the target group:

```bash
aws autoscaling attach-load-balancer-target-groups \
  --auto-scaling-group-name LexiAI-ASG \
  --target-group-arns <target-group-arn>
```

## Step 12: Set Up CI/CD with AWS CodePipeline (Optional)

1. Create a CodeCommit repository:

```bash
aws codecommit create-repository --repository-name lexiai --repository-description "LexiAI application repository"
```

2. Create a CodeBuild project:

```bash
aws codebuild create-project \
  --name LexiAI-Build \
  --source type=CODECOMMIT,location=<codecommit-repo-url> \
  --artifacts type=NO_ARTIFACTS \
  --environment type=LINUX_CONTAINER,image=aws/codebuild/amazonlinux2-x86_64-standard:3.0,computeType=BUILD_GENERAL1_SMALL,privilegedMode=true \
  --service-role <codebuild-service-role-arn>
```

3. Create a CodeDeploy application:

```bash
aws deploy create-application --application-name LexiAI
```

4. Create a CodeDeploy deployment group:

```bash
aws deploy create-deployment-group \
  --application-name LexiAI \
  --deployment-group-name LexiAI-DeploymentGroup \
  --deployment-config-name CodeDeployDefault.OneAtATime \
  --ec2-tag-filters Key=Name,Value=LexiAI-App,Type=KEY_AND_VALUE \
  --service-role-arn <codedeploy-service-role-arn>
```

5. Create a CodePipeline pipeline:

```bash
aws codepipeline create-pipeline \
  --pipeline-name LexiAI-Pipeline \
  --role-arn <codepipeline-service-role-arn> \
  --artifact-store type=S3,location=<artifact-bucket-name> \
  --stages '[
    {
      "name": "Source",
      "actions": [
        {
          "name": "Source",
          "actionTypeId": {
            "category": "Source",
            "owner": "AWS",
            "provider": "CodeCommit",
            "version": "1"
          },
          "configuration": {
            "RepositoryName": "lexiai",
            "BranchName": "main"
          },
          "outputArtifacts": [
            {
              "name": "SourceCode"
            }
          ]
        }
      ]
    },
    {
      "name": "Build",
      "actions": [
        {
          "name": "BuildAction",
          "actionTypeId": {
            "category": "Build",
            "owner": "AWS",
            "provider": "CodeBuild",
            "version": "1"
          },
          "configuration": {
            "ProjectName": "LexiAI-Build"
          },
          "inputArtifacts": [
            {
              "name": "SourceCode"
            }
          ],
          "outputArtifacts": [
            {
              "name": "BuildOutput"
            }
          ]
        }
      ]
    },
    {
      "name": "Deploy",
      "actions": [
        {
          "name": "DeployAction",
          "actionTypeId": {
            "category": "Deploy",
            "owner": "AWS",
            "provider": "CodeDeploy",
            "version": "1"
          },
          "configuration": {
            "ApplicationName": "LexiAI",
            "DeploymentGroupName": "LexiAI-DeploymentGroup"
          },
          "inputArtifacts": [
            {
              "name": "BuildOutput"
            }
          ]
        }
      ]
    }
  ]'
```

## Conclusion

You have now deployed the LexiAI application to AWS with a scalable, secure, and highly available architecture. The application is accessible via your domain name and protected with SSL.

For ongoing maintenance and operations:

1. Regularly update the EC2 instances with security patches
2. Monitor the application performance using CloudWatch
3. Set up automated backups for the RDS database
4. Implement a disaster recovery plan
5. Consider using AWS Secrets Manager for sensitive configuration values

For any issues or questions, please refer to the AWS documentation or contact your system administrator.

