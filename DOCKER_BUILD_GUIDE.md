# Docker Build Guide for Sudoku Game

This guide provides step-by-step instructions for building the Docker image for the Sudoku game.

## Prerequisites

- Docker installed on your system
  - Windows: Docker Desktop for Windows
  - Linux: Docker Engine
  - Mac: Docker Desktop for Mac
- Basic command line knowledge

## Verify Docker Installation

Check if Docker is installed and running:

```bash
docker --version
docker info
```

Expected output should show Docker version (e.g., Docker version 24.0.x).

## Project Structure

Ensure your project has the following structure:

```
demo-project/
├── sudoku_game.py
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

## Building the Docker Image

### Option 1: Basic Build

Build the Docker image with a tag:

```bash
# Navigate to project directory
cd D:/DevOps_fall-25/demo-project

# Build the image
docker build -t sudoku-game:latest .
```

**Explanation:**
- `docker build`: Docker command to build an image
- `-t sudoku-game:latest`: Tag the image with name "sudoku-game" and version "latest"
- `.`: Use current directory as build context

### Option 2: Build with Custom Tag

Build with a specific version tag:

```bash
docker build -t sudoku-game:v1.0 .
```

### Option 3: Build with Multiple Tags

Build and tag with multiple names:

```bash
docker build -t sudoku-game:latest -t sudoku-game:v1.0 -t sudoku-game:stable .
```

### Option 4: Build with Build Arguments

If you want to pass build-time variables:

```bash
docker build --build-arg PYTHON_VERSION=3.11 -t sudoku-game:latest .
```

## Verify the Build

### 1. List Docker Images

Check if the image was created successfully:

```bash
docker images
```

You should see output like:

```
REPOSITORY     TAG       IMAGE ID       CREATED          SIZE
sudoku-game    latest    abc123def456   10 seconds ago   150MB
```

### 2. Inspect the Image

Get detailed information about the image:

```bash
docker inspect sudoku-game:latest
```

### 3. Check Image History

View the layers and build history:

```bash
docker history sudoku-game:latest
```

## Test the Docker Image

### Run the Container Interactively

Test the game by running the container:

```bash
docker run -it sudoku-game:latest
```

**Explanation:**
- `-i`: Keep STDIN open (interactive)
- `-t`: Allocate a pseudo-TTY (terminal)

### Run with Custom Name

Run with a specific container name:

```bash
docker run -it --name my-sudoku-game sudoku-game:latest
```

### Run in Detached Mode (Background)

For testing purposes (though not useful for interactive game):

```bash
docker run -d --name sudoku-background sudoku-game:latest
```

Stop the container:

```bash
docker stop sudoku-background
docker rm sudoku-background
```

## Build Optimization Tips

### 1. Use BuildKit (Recommended)

Enable Docker BuildKit for faster builds:

```bash
# Linux/Mac
DOCKER_BUILDKIT=1 docker build -t sudoku-game:latest .

# Windows PowerShell
$env:DOCKER_BUILDKIT=1
docker build -t sudoku-game:latest .

# Windows CMD
set DOCKER_BUILDKIT=1
docker build -t sudoku-game:latest .
```

### 2. No Cache Build

Force rebuild without using cache:

```bash
docker build --no-cache -t sudoku-game:latest .
```

### 3. Build with Progress Output

Show detailed build progress:

```bash
docker build --progress=plain -t sudoku-game:latest .
```

## Troubleshooting

### Build Fails with "Cannot find Dockerfile"

Ensure you're in the correct directory:

```bash
pwd  # Linux/Mac
cd   # Windows

# Navigate to project directory
cd D:/DevOps_fall-25/demo-project
```

### Build Fails with Permission Denied

**Linux/Mac**: Run with sudo or add user to docker group:

```bash
sudo docker build -t sudoku-game:latest .

# Or add user to docker group (requires logout/login)
sudo usermod -aG docker $USER
```

**Windows**: Run Docker Desktop as Administrator

### Build is Very Slow

- Enable BuildKit (see above)
- Check .dockerignore file to exclude unnecessary files
- Use faster internet connection for base image download

### Out of Disk Space

Clean up old images and containers:

```bash
# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a

# Check disk usage
docker system df
```

## Image Size Optimization

### Check Image Size

```bash
docker images sudoku-game
```

### Reduce Image Size

The Dockerfile already uses:
- Multi-stage builds
- Slim base image (python:3.11-slim)
- No cache during pip install

### Compare Image Sizes

```bash
# Build with alpine (smaller)
docker build -f Dockerfile.alpine -t sudoku-game:alpine .

# Compare sizes
docker images | grep sudoku-game
```

## Next Steps

After successfully building the image:

1. Test the game thoroughly
2. Tag the image for your registry (see GHCR_PUSH_GUIDE.md)
3. Push to GitHub Container Registry
4. Deploy to AWS EC2

## Quick Reference Commands

```bash
# Build
docker build -t sudoku-game:latest .

# List images
docker images

# Run interactively
docker run -it sudoku-game:latest

# Remove image
docker rmi sudoku-game:latest

# Clean up
docker system prune -a
```

## Additional Resources

- [Docker Build Documentation](https://docs.docker.com/engine/reference/commandline/build/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker BuildKit](https://docs.docker.com/build/buildkit/)
