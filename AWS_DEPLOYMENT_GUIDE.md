# AWS EC2 Deployment Guide for Sudoku Game

This guide provides step-by-step instructions for deploying your Sudoku game Docker container on AWS EC2.

## Prerequisites

- AWS account (free tier eligible)
- Docker image pushed to GHCR (see GHCR_PUSH_GUIDE.md)
- Basic understanding of AWS services
- SSH client installed on your local machine

## Part 1: Create and Configure EC2 Instance

### Step 1.1: Sign in to AWS Console

1. Go to [AWS Console](https://console.aws.amazon.com)
2. Sign in with your credentials
3. Select your preferred region (e.g., us-east-1) from top-right dropdown

### Step 1.2: Launch EC2 Instance

1. Navigate to EC2 service:
   - Search for "EC2" in the search bar
   - Click **EC2** under Services

2. Click **Launch Instance** button

### Step 1.3: Configure Instance Details

#### Name and Tags

```
Name: sudoku-game-server
```

#### Application and OS Images (AMI)

Select **Amazon Linux 2023** or **Ubuntu Server 22.04 LTS**:

- **Amazon Linux 2023** (Recommended)
  - AMI: Amazon Linux 2023 AMI
  - Architecture: 64-bit (x86)

- **Ubuntu Server 22.04 LTS** (Alternative)
  - AMI: Ubuntu Server 22.04 LTS
  - Architecture: 64-bit (x86)

#### Instance Type

Select: **t2.micro** (Free tier eligible)
- vCPUs: 1
- Memory: 1 GiB
- Network Performance: Low to Moderate

For better performance (not free tier):
- **t3.small**: 2 vCPUs, 2 GiB RAM
- **t3.medium**: 2 vCPUs, 4 GiB RAM

#### Key Pair (Login)

1. Click **Create new key pair**
2. Settings:
   - **Key pair name**: `sudoku-game-key`
   - **Key pair type**: RSA
   - **Private key file format**:
     - `.pem` (for Linux/Mac/Windows with OpenSSH)
     - `.ppk` (for Windows with PuTTY)
3. Click **Create key pair**
4. **Save the downloaded file securely** (you'll need it for SSH)

#### Network Settings

Click **Edit** and configure:

1. **VPC**: Default VPC (or create new)
2. **Subnet**: No preference (default)
3. **Auto-assign public IP**: Enable
4. **Firewall (Security Groups)**: Create security group
   - **Security group name**: `sudoku-game-sg`
   - **Description**: Security group for Sudoku game server

**Security Group Rules**:

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| Custom TCP | TCP | 8080 | 0.0.0.0/0 | Application port |
| Custom TCP | TCP | 9090 | My IP | Prometheus |
| Custom TCP | TCP | 3000 | My IP | Grafana |
| Custom TCP | TCP | 9100 | My IP | Node Exporter |

5. Click **Add security group rule** for each rule above

#### Configure Storage

- **Size**: 8 GiB (minimum) - 20 GiB (recommended)
- **Volume Type**: gp3 (General Purpose SSD)
- **Delete on Termination**: Yes

#### Advanced Details (Optional)

Leave as default or configure:
- **IAM instance profile**: None (or create if needed)
- **User data**: Leave empty (we'll install manually)

### Step 1.4: Launch Instance

1. Review configuration summary
2. Click **Launch instance**
3. Wait for instance to be in "Running" state (2-3 minutes)

### Step 1.5: Note Instance Details

Once instance is running:

1. Select your instance
2. Note down:
   - **Instance ID**: `i-0123456789abcdef0`
   - **Public IPv4 address**: `3.231.xxx.xxx`
   - **Public IPv4 DNS**: `ec2-3-231-xxx-xxx.compute-1.amazonaws.com`

## Part 2: Connect to EC2 Instance

### Step 2.1: Set Key Pair Permissions (Linux/Mac)

```bash
# Navigate to where you saved the key
cd ~/Downloads

# Set proper permissions
chmod 400 sudoku-game-key.pem
```

### Step 2.2: Connect via SSH

#### Option 1: Direct SSH (Linux/Mac/Windows with OpenSSH)

```bash
ssh -i "sudoku-game-key.pem" ec2-user@YOUR_INSTANCE_PUBLIC_IP
```

**For Amazon Linux 2023**:

```bash
ssh -i "sudoku-game-key.pem" ec2-user@3.231.xxx.xxx
```

**For Ubuntu**:

```bash
ssh -i "sudoku-game-key.pem" ubuntu@3.231.xxx.xxx
```

#### Option 2: Using EC2 Instance Connect (Browser-based)

1. Go to EC2 Console
2. Select your instance
3. Click **Connect** button
4. Choose **EC2 Instance Connect** tab
5. Click **Connect** button

#### Option 3: Using PuTTY (Windows)

1. Open PuTTY
2. Session settings:
   - **Host Name**: `ec2-user@YOUR_INSTANCE_PUBLIC_IP`
   - **Port**: 22
3. Connection → SSH → Auth:
   - Browse and select your `.ppk` file
4. Click **Open**

### Step 2.3: Verify Connection

Once connected, you should see:

```
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'

[ec2-user@ip-xxx-xxx-xxx-xxx ~]$
```

## Part 3: Install Docker on EC2

### Step 3.1: Update System Packages

**For Amazon Linux 2023**:

```bash
sudo yum update -y
```

**For Ubuntu**:

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 3.2: Install Docker

**For Amazon Linux 2023**:

```bash
# Install Docker
sudo yum install docker -y

# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Verify Docker is running
sudo systemctl status docker
```

**For Ubuntu**:

```bash
# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 3.3: Add User to Docker Group

```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes (logout and login, or use newgrp)
newgrp docker

# Verify you can run docker without sudo
docker --version
docker info
```

Expected output:

```
Docker version 24.0.x, build xxxxx
```

## Part 4: Pull and Run Docker Container

### Step 4.1: Login to GHCR (if private image)

If your image is private:

```bash
# Login to GHCR
docker login ghcr.io -u YOUR_GITHUB_USERNAME

# Enter your GitHub Personal Access Token when prompted
```

### Step 4.2: Pull Docker Image

```bash
# Pull your image from GHCR
docker pull ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

Example:

```bash
docker pull ghcr.io/john-doe/sudoku-game:latest
```

### Step 4.3: Verify Image

```bash
docker images
```

Expected output:

```
REPOSITORY                           TAG       IMAGE ID       CREATED        SIZE
ghcr.io/john-doe/sudoku-game        latest    abc123def456   2 hours ago    150MB
```

### Step 4.4: Run Container Interactively

```bash
# Run the container
docker run -it --name sudoku-game ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

To exit the game and container: Type `quit` in the game

### Step 4.5: Run Container as Detached Service (Background)

For a web-based version (future enhancement):

```bash
# Run in detached mode
docker run -d \
  --name sudoku-game \
  -p 8080:8080 \
  --restart unless-stopped \
  ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

**Explanation**:
- `-d`: Detached mode (background)
- `--name`: Container name
- `-p 8080:8080`: Port mapping (host:container)
- `--restart unless-stopped`: Auto-restart policy

### Step 4.6: Manage Container

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Stop container
docker stop sudoku-game

# Start container
docker start sudoku-game

# Restart container
docker restart sudoku-game

# View container logs
docker logs sudoku-game

# Follow logs in real-time
docker logs -f sudoku-game

# Remove container
docker rm sudoku-game

# Remove container (force)
docker rm -f sudoku-game
```

## Part 5: Create Persistent Setup

### Step 5.1: Create Systemd Service (Optional)

For auto-start on boot, create a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/sudoku-game.service
```

Add the following content:

```ini
[Unit]
Description=Sudoku Game Docker Container
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=-/usr/bin/docker stop sudoku-game
ExecStartPre=-/usr/bin/docker rm sudoku-game
ExecStart=/usr/bin/docker run \
  --name sudoku-game \
  -p 8080:8080 \
  ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
ExecStop=/usr/bin/docker stop sudoku-game

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable sudoku-game.service

# Start service
sudo systemctl start sudoku-game.service

# Check status
sudo systemctl status sudoku-game.service
```

### Step 5.2: Create Docker Compose Setup (Alternative)

Install Docker Compose:

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

Create `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Add:

```yaml
version: '3.8'

services:
  sudoku-game:
    image: ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
    container_name: sudoku-game
    ports:
      - "8080:8080"
    restart: unless-stopped
    stdin_open: true
    tty: true
```

Run with Docker Compose:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Part 6: Access and Test

### Step 6.1: Access from EC2

```bash
# Connect to running container
docker exec -it sudoku-game /bin/bash

# Or run the game directly
docker run -it ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

### Step 6.2: Access from Local Machine (SSH Tunnel)

For interactive terminal access:

```bash
# From your local machine
ssh -i "sudoku-game-key.pem" -t ec2-user@YOUR_INSTANCE_PUBLIC_IP "docker run -it ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest"
```

## Part 7: Update and Maintenance

### Step 7.1: Update Docker Image

```bash
# Pull latest image
docker pull ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

# Stop and remove old container
docker stop sudoku-game
docker rm sudoku-game

# Run new container
docker run -d --name sudoku-game -p 8080:8080 ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

### Step 7.2: Automate Updates

Create update script:

```bash
nano update-sudoku.sh
```

Add:

```bash
#!/bin/bash

echo "Pulling latest image..."
docker pull ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

echo "Stopping container..."
docker stop sudoku-game

echo "Removing old container..."
docker rm sudoku-game

echo "Starting new container..."
docker run -d \
  --name sudoku-game \
  -p 8080:8080 \
  --restart unless-stopped \
  ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

echo "Update complete!"
docker ps | grep sudoku-game
```

Make executable:

```bash
chmod +x update-sudoku.sh
./update-sudoku.sh
```

## Part 8: Security Best Practices

### Step 8.1: Configure Firewall

```bash
# Enable firewall (Amazon Linux)
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Allow SSH
sudo firewall-cmd --permanent --add-service=ssh

# Allow custom port
sudo firewall-cmd --permanent --add-port=8080/tcp

# Reload firewall
sudo firewall-cmd --reload
```

### Step 8.2: Keep System Updated

```bash
# Set up automatic updates (Amazon Linux)
sudo yum install -y yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

### Step 8.3: Monitor Security

```bash
# Check for security updates
sudo yum check-update --security

# Install security updates only
sudo yum update --security -y
```

## Troubleshooting

### Can't Connect via SSH

**Solutions**:
- Verify security group allows SSH (port 22) from your IP
- Check key file permissions: `chmod 400 sudoku-game-key.pem`
- Verify instance is running
- Check public IP address is correct

### Docker Command Not Found

**Solutions**:
```bash
# Verify Docker is installed
which docker

# Install Docker (if missing)
sudo yum install docker -y
sudo systemctl start docker
```

### Permission Denied (Docker)

**Solutions**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login, or use:
newgrp docker
```

### Container Exits Immediately

**Solutions**:
```bash
# Check logs
docker logs sudoku-game

# Run interactively for debugging
docker run -it ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

### Out of Disk Space

**Solutions**:
```bash
# Clean up Docker
docker system prune -a

# Check disk usage
df -h
```

## Cost Optimization

### Free Tier Limits

- **EC2**: 750 hours/month of t2.micro
- **EBS**: 30 GB storage
- **Data Transfer**: 15 GB outbound per month

### Stop Instance When Not in Use

```bash
# From AWS Console
# Select instance → Instance state → Stop instance

# From AWS CLI (install aws-cli first)
aws ec2 stop-instances --instance-ids i-0123456789abcdef0
```

### Terminate Instance

**WARNING**: This will delete the instance permanently

```bash
# From AWS Console
# Select instance → Instance state → Terminate instance
```

## Quick Reference Commands

```bash
# SSH to EC2
ssh -i "sudoku-game-key.pem" ec2-user@YOUR_IP

# Pull image
docker pull ghcr.io/USERNAME/sudoku-game:latest

# Run container
docker run -it ghcr.io/USERNAME/sudoku-game:latest

# Run detached
docker run -d --name sudoku-game -p 8080:8080 ghcr.io/USERNAME/sudoku-game:latest

# Container management
docker ps
docker logs sudoku-game
docker stop sudoku-game
docker start sudoku-game
docker rm sudoku-game

# System maintenance
sudo yum update -y
docker system prune -a
```

## Next Steps

After successful deployment:

1. Set up monitoring (see MONITORING_GUIDE.md)
2. Configure automated backups
3. Set up CloudWatch alarms
4. Implement CI/CD pipeline
5. Add SSL/TLS certificates (for web version)

## Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Docker on AWS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html)
- [EC2 Instance Connect](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Connect-using-EC2-Instance-Connect.html)
