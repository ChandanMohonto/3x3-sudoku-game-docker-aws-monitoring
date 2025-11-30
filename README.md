# Sudoku Puzzle Game - Complete DevOps Project

A fully containerized Sudoku puzzle game with complete deployment pipeline to AWS and comprehensive monitoring setup.

## Project Overview

This project demonstrates a complete DevOps workflow including:
- Python application development (Sudoku game)
- Docker containerization
- Container registry management (GitHub Container Registry)
- Cloud deployment (AWS EC2)
- Infrastructure monitoring (Prometheus + Grafana)
- System metrics collection (Node Exporter)

## Features

### Sudoku Game Features
- Interactive command-line Sudoku puzzle game
- Multiple difficulty levels (Easy, Medium, Hard)
- Auto-generated puzzles with unique solutions
- Backtracking solver algorithm
- Hint system
- Move tracking and timer

### DevOps Features
- Containerized application with Docker
- Multi-stage Docker build for optimization
- Automated deployment to cloud
- Comprehensive monitoring stack
- System and container metrics
- Real-time dashboards

## Project Structure

```
demo-project/
├── sudoku_game.py              # Main Sudoku game application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── .dockerignore              # Docker build exclusions
├── README.md                  # This file
├── DOCKER_BUILD_GUIDE.md      # Step-by-step Docker build instructions
├── GHCR_PUSH_GUIDE.md         # GitHub Container Registry guide
├── AWS_DEPLOYMENT_GUIDE.md    # AWS EC2 deployment instructions
└── MONITORING_GUIDE.md        # Complete monitoring setup guide
```

## Quick Start

### 1. Run Locally (Python)

```bash
# Clone or navigate to project directory
cd demo-project

# Run the game
python3 sudoku_game.py

# Choose difficulty and play!
```

### 2. Run with Docker

```bash
# Build the image
docker build -t sudoku-game:latest .

# Run the container
docker run -it sudoku-game:latest
```

## Complete Workflow

### Step 1: Build Docker Image

Follow the detailed guide in [DOCKER_BUILD_GUIDE.md](DOCKER_BUILD_GUIDE.md)

**Quick commands**:
```bash
docker build -t sudoku-game:latest .
docker images
docker run -it sudoku-game:latest
```

### Step 2: Push to GitHub Container Registry

Follow the detailed guide in [GHCR_PUSH_GUIDE.md](GHCR_PUSH_GUIDE.md)

**Quick commands**:
```bash
# Login to GHCR
docker login ghcr.io -u YOUR_GITHUB_USERNAME

# Tag the image
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

# Push to GHCR
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

### Step 3: Deploy to AWS EC2

Follow the detailed guide in [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)

**Overview**:
1. Create EC2 instance (t2.micro - Free tier eligible)
2. Configure security groups
3. Install Docker on EC2
4. Pull and run your image

**Quick commands** (on EC2):
```bash
# Pull image
docker pull ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

# Run container
docker run -it ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

### Step 4: Set Up Monitoring

Follow the detailed guide in [MONITORING_GUIDE.md](MONITORING_GUIDE.md)

**Components**:
- **Node Exporter**: System metrics (CPU, memory, disk)
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization dashboards
- **cAdvisor**: Docker container metrics

**Access URLs** (after setup):
- Grafana: `http://YOUR_EC2_IP:3000`
- Prometheus: `http://YOUR_EC2_IP:9090`
- Node Exporter: `http://YOUR_EC2_IP:9100/metrics`

## Documentation

Each guide provides comprehensive, step-by-step instructions with code examples:

### 📘 [Docker Build Guide](DOCKER_BUILD_GUIDE.md)
- Docker installation verification
- Building images with various options
- Image optimization techniques
- Testing and troubleshooting
- Best practices

### 📙 [GHCR Push Guide](GHCR_PUSH_GUIDE.md)
- Creating GitHub Personal Access Token
- Authenticating with GHCR
- Tagging and pushing images
- Making packages public/private
- Automation with GitHub Actions
- Security best practices

### 📗 [AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md)
- Creating EC2 instance
- Security group configuration
- SSH connection methods
- Docker installation on EC2
- Container deployment
- Systemd service setup
- Maintenance and updates
- Cost optimization

### 📕 [Monitoring Guide](MONITORING_GUIDE.md)
- Node Exporter installation and configuration
- Prometheus setup and configuration
- Grafana installation and dashboards
- cAdvisor for container metrics
- Alert rule configuration
- Docker Compose setup
- Performance tuning
- Troubleshooting

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Developer                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 1. Build & Push
                     ▼
         ┌───────────────────────────┐
         │  GitHub Container Registry │
         │  (GHCR)                   │
         └───────────┬───────────────┘
                     │
                     │ 2. Deploy
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     AWS EC2 Instance                         │
│                                                               │
│  ┌──────────────┐    ┌───────────────┐    ┌─────────────┐  │
│  │ Sudoku Game  │◄───│  Docker       │◄───│  cAdvisor   │  │
│  │ Container    │    │  Engine       │    │  (Metrics)  │  │
│  └──────────────┘    └───────────────┘    └──────┬──────┘  │
│                                                    │          │
│  ┌───────────────┐                                │          │
│  │ Node Exporter │                                │          │
│  │ (System       │                                │          │
│  │  Metrics)     │                                │          │
│  └───────┬───────┘                                │          │
│          │                                         │          │
│          │         ┌──────────────┐                │          │
│          └────────►│  Prometheus  │◄───────────────┘          │
│                    │  (Metrics    │                           │
│                    │   Storage)   │                           │
│                    └──────┬───────┘                           │
│                           │                                   │
│                           ▼                                   │
│                    ┌──────────────┐                           │
│                    │   Grafana    │                           │
│                    │  (Dashboard) │                           │
│                    └──────────────┘                           │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
                            │ 3. Monitor
                            ▼
                    ┌───────────────┐
                    │  Admin/User   │
                    │  Dashboard    │
                    └───────────────┘
```

## Technologies Used

### Application
- **Python 3.11**: Programming language
- **Standard Library**: No external dependencies

### Containerization
- **Docker**: Container platform
- **Multi-stage builds**: Image optimization

### Container Registry
- **GitHub Container Registry (GHCR)**: Image storage and distribution

### Cloud Platform
- **AWS EC2**: Virtual server hosting
- **Amazon Linux 2023**: Operating system

### Monitoring Stack
- **Node Exporter**: System metrics exporter
- **Prometheus**: Metrics collection and storage
- **Grafana**: Metrics visualization
- **cAdvisor**: Container metrics

## Requirements

### Development
- Python 3.11 or higher
- Docker Desktop or Docker Engine
- Git

### Deployment
- AWS Account (Free tier eligible)
- GitHub Account
- SSH client

### Monitoring
- 20GB+ disk space on EC2
- t2.micro or larger instance (for monitoring stack)

## Game Instructions

### Starting the Game

```bash
# Run locally
python3 sudoku_game.py

# Or with Docker
docker run -it sudoku-game:latest
```

### How to Play

1. **Choose Difficulty**: Select easy, medium, or hard
2. **View the Board**: Numbers 1-9 represent filled cells, dots (.) represent empty cells
3. **Make Moves**: Enter `row col number` (e.g., `5 3 7`)
4. **Get Hints**: Type `hint` for a suggestion
5. **View Solution**: Type `solve` to see the complete solution
6. **New Game**: Type `new` to start a fresh puzzle
7. **Quit**: Type `quit` to exit

### Game Rules

- Fill the 9x9 grid with numbers 1-9
- Each row must contain all digits 1-9
- Each column must contain all digits 1-9
- Each 3x3 box must contain all digits 1-9

## Monitoring Metrics

After setting up monitoring, you can track:

### System Metrics (Node Exporter)
- CPU usage and load average
- Memory usage and swap
- Disk I/O and space
- Network traffic
- System uptime

### Container Metrics (cAdvisor)
- Container CPU usage
- Container memory usage
- Container network I/O
- Container filesystem usage
- Container restart count

### Application Metrics (Custom)
- Game sessions
- User moves
- Puzzle difficulty distribution
- Completion times

## Security Considerations

### Docker Security
- Using non-root user (multi-stage build)
- Minimal base image (python:3.11-slim)
- .dockerignore to exclude sensitive files

### AWS Security
- Security groups with minimal open ports
- SSH key-based authentication
- Regular system updates
- Firewall configuration

### GHCR Security
- Personal Access Token with minimal permissions
- Token rotation recommended
- Private repositories by default

## Troubleshooting

### Common Issues

**Docker build fails**:
- Check Docker is running: `docker info`
- Verify Dockerfile syntax
- Check available disk space

**Can't push to GHCR**:
- Verify PAT has `write:packages` permission
- Check image name is lowercase
- Ensure you're logged in: `docker login ghcr.io`

**Can't connect to EC2**:
- Verify security group allows SSH (port 22)
- Check key file permissions: `chmod 400 key.pem`
- Verify instance is running

**Monitoring not working**:
- Check all services are running
- Verify ports are open in security group
- Check service logs: `journalctl -u service-name`

For detailed troubleshooting, see respective guide documents.

## Performance Optimization

### Docker Image
- Multi-stage build reduces size
- Slim base image (150MB vs 900MB+)
- Layer caching optimization

### AWS EC2
- Choose appropriate instance size
- Enable CloudWatch monitoring
- Use Elastic IPs for static addressing

### Monitoring
- Adjust scrape intervals
- Configure data retention
- Use dashboard filters

## Cost Estimation

### Free Tier (First 12 months)
- **EC2 t2.micro**: 750 hours/month (FREE)
- **EBS Storage**: 30 GB (FREE)
- **Data Transfer**: 15 GB outbound (FREE)
- **GHCR**: Unlimited public images (FREE)

### After Free Tier
- **EC2 t2.micro**: ~$8/month
- **EBS 20GB**: ~$2/month
- **Data Transfer**: ~$1/GB
- **Total**: ~$10-15/month

### Cost Optimization
- Stop instance when not in use
- Use reserved instances for long-term
- Enable CloudWatch billing alarms

## Future Enhancements

- [ ] Web-based UI (React/Flask)
- [ ] User authentication and profiles
- [ ] Leaderboard and statistics
- [ ] Multi-player support
- [ ] Mobile app version
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Automated testing
- [ ] Database integration
- [ ] SSL/TLS encryption
- [ ] Load balancing with multiple instances

## Contributing

Feel free to fork this project and submit pull requests for:
- Bug fixes
- New features
- Documentation improvements
- Performance optimizations

## License

This project is open source and available for educational purposes.

## Support

For issues or questions:
1. Check the relevant guide document
2. Review troubleshooting sections
3. Check service logs
4. Open an issue on GitHub

## Acknowledgments

- Sudoku puzzle algorithm based on backtracking method
- Monitoring stack inspired by Prometheus best practices
- Docker configuration follows official guidelines
- AWS deployment based on AWS best practices

## Quick Reference Card

### Essential Commands

```bash
# Local Development
python3 sudoku_game.py

# Docker
docker build -t sudoku-game:latest .
docker run -it sudoku-game:latest
docker push ghcr.io/USERNAME/sudoku-game:latest

# AWS (on EC2)
docker pull ghcr.io/USERNAME/sudoku-game:latest
docker run -it ghcr.io/USERNAME/sudoku-game:latest

# Monitoring
sudo systemctl status node_exporter
sudo systemctl status prometheus
sudo systemctl status grafana-server
```

### Access URLs

| Service | URL | Port |
|---------|-----|------|
| Sudoku Game | http://YOUR_IP:8080 | 8080 |
| Grafana | http://YOUR_IP:3000 | 3000 |
| Prometheus | http://YOUR_IP:9090 | 9090 |
| Node Exporter | http://YOUR_IP:9100 | 9100 |
| cAdvisor | http://YOUR_IP:8081 | 8081 |

### Important Files

```
Application:
- sudoku_game.py
- requirements.txt
- Dockerfile

Configuration:
- /etc/prometheus/prometheus.yml
- /etc/grafana/grafana.ini

Logs:
- /var/log/prometheus/
- /var/log/grafana/
```

## Project Timeline

Estimated time to complete entire setup:

1. **Build Application**: 30 minutes (already done!)
2. **Dockerize**: 15 minutes
3. **Push to GHCR**: 10 minutes
4. **Deploy to AWS**: 30 minutes
5. **Setup Monitoring**: 45 minutes

**Total**: ~2-3 hours for complete setup

---

**Happy Coding and Gaming!** 🎮

For detailed instructions, please refer to the individual guide documents.
