# GitHub Container Registry (GHCR) Push Guide

This guide provides step-by-step instructions for pushing your Sudoku game Docker image to GitHub Container Registry.

## Prerequisites

- GitHub account
- Docker image built locally (see DOCKER_BUILD_GUIDE.md)
- Git installed on your system
- Docker installed and running

## Step 1: Create GitHub Personal Access Token (PAT)

### 1.1 Navigate to GitHub Settings

1. Go to [GitHub](https://github.com)
2. Click your profile picture (top right)
3. Click **Settings**
4. Scroll down and click **Developer settings** (bottom left)
5. Click **Personal access tokens** → **Tokens (classic)**
6. Click **Generate new token** → **Generate new token (classic)**

### 1.2 Configure Token Permissions

Set the following:

- **Note**: `GHCR Access Token` (or any descriptive name)
- **Expiration**: Select expiration period (e.g., 90 days)
- **Scopes**: Check these boxes:
  - ✅ `write:packages` - Upload packages to GitHub Package Registry
  - ✅ `read:packages` - Download packages from GitHub Package Registry
  - ✅ `delete:packages` - Delete packages from GitHub Package Registry (optional)
  - ✅ `repo` - Full control of private repositories (if using private repos)

### 1.3 Generate and Save Token

1. Click **Generate token** at the bottom
2. **IMPORTANT**: Copy the token immediately (it won't be shown again)
3. Save it securely (e.g., password manager)

Example token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 2: Authenticate Docker with GHCR

### Option 1: Interactive Login (Recommended)

```bash
# Login to GHCR
docker login ghcr.io -u YOUR_GITHUB_USERNAME

# When prompted for password, paste your Personal Access Token
```

**Example:**

```bash
docker login ghcr.io -u john-doe
Password: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Expected output:

```
Login Succeeded
```

### Option 2: Non-Interactive Login

```bash
# Using echo
echo "YOUR_PAT_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

**Example:**

```bash
echo "ghp_xxxxxxxxxxxx" | docker login ghcr.io -u john-doe --password-stdin
```

### Option 3: Using Environment Variable

```bash
# Linux/Mac
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
echo $env:GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Verify Login

Check Docker credentials:

```bash
# Linux/Mac
cat ~/.docker/config.json

# Windows
type %USERPROFILE%\.docker\config.json
```

## Step 3: Tag Your Docker Image for GHCR

### 3.1 Understand GHCR Image Naming

GHCR images follow this format:

```
ghcr.io/OWNER/IMAGE_NAME:TAG
```

Where:
- `OWNER`: Your GitHub username or organization name (lowercase)
- `IMAGE_NAME`: Name of your image (lowercase)
- `TAG`: Version tag (e.g., latest, v1.0, stable)

### 3.2 Tag the Image

```bash
# Basic format
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

# Example
docker tag sudoku-game:latest ghcr.io/john-doe/sudoku-game:latest
```

### 3.3 Tag with Multiple Versions

```bash
# Tag with latest
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest

# Tag with version
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:v1.0

# Tag with custom tags
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:stable
```

### 3.4 Verify Tags

```bash
docker images | grep sudoku-game
```

Expected output:

```
REPOSITORY                              TAG       IMAGE ID       CREATED         SIZE
sudoku-game                             latest    abc123def456   5 minutes ago   150MB
ghcr.io/john-doe/sudoku-game           latest    abc123def456   5 minutes ago   150MB
ghcr.io/john-doe/sudoku-game           v1.0      abc123def456   5 minutes ago   150MB
```

## Step 4: Push Image to GHCR

### 4.1 Push Single Tag

```bash
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

**Example:**

```bash
docker push ghcr.io/john-doe/sudoku-game:latest
```

Expected output:

```
The push refers to repository [ghcr.io/john-doe/sudoku-game]
5f70bf18a086: Pushed
d8d1f1e7b2a3: Pushed
latest: digest: sha256:abc123... size: 1234
```

### 4.2 Push Multiple Tags

```bash
# Push all tags
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:v1.0
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:stable
```

### 4.3 Push All Tags at Once

```bash
# Push all tags for an image
docker push --all-tags ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game
```

## Step 5: Verify Push on GitHub

### 5.1 View Package on GitHub

1. Go to your GitHub profile: `https://github.com/YOUR_USERNAME`
2. Click on **Packages** tab
3. You should see `sudoku-game` package listed

Or directly visit:

```
https://github.com/YOUR_USERNAME?tab=packages
```

### 5.2 View Package Details

Visit:

```
https://github.com/users/YOUR_USERNAME/packages/container/sudoku-game
```

### 5.3 Make Package Public (Optional)

By default, packages are private. To make public:

1. Go to package page
2. Click **Package settings** (right sidebar)
3. Scroll to **Danger Zone**
4. Click **Change visibility**
5. Select **Public**
6. Type package name to confirm
7. Click **I understand, change package visibility**

## Step 6: Pull Image from GHCR (Test)

### 6.1 Remove Local Image (Optional)

```bash
# Remove local images to test pull
docker rmi ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
docker rmi sudoku-game:latest
```

### 6.2 Pull from GHCR

```bash
# Pull the image
docker pull ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

### 6.3 Run Pulled Image

```bash
docker run -it ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

## Complete Workflow Example

Here's the complete workflow from build to push:

```bash
# Step 1: Build the image
docker build -t sudoku-game:latest .

# Step 2: Login to GHCR
docker login ghcr.io -u YOUR_GITHUB_USERNAME
# Enter your PAT when prompted

# Step 3: Tag the image
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
docker tag sudoku-game:latest ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:v1.0

# Step 4: Push to GHCR
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
docker push ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:v1.0

# Step 5: Verify
docker pull ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
docker run -it ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
```

## Automation with GitHub Actions (Optional)

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## Troubleshooting

### Error: "denied: permission_denied"

**Solution**: Check your PAT has correct permissions (`write:packages`)

### Error: "unauthorized: authentication required"

**Solution**: Login again to GHCR:

```bash
docker logout ghcr.io
docker login ghcr.io -u YOUR_GITHUB_USERNAME
```

### Error: "invalid reference format"

**Solution**: Ensure image name is lowercase:

```bash
# Incorrect
docker tag sudoku-game:latest ghcr.io/John-Doe/Sudoku-Game:latest

# Correct
docker tag sudoku-game:latest ghcr.io/john-doe/sudoku-game:latest
```

### Push is Very Slow

**Solutions**:
- Check internet connection
- Try pushing during off-peak hours
- Compress layers better in Dockerfile

### Can't Find Package on GitHub

**Solutions**:
- Wait a few minutes for indexing
- Check package visibility settings
- Verify push completed successfully

## Security Best Practices

### 1. Token Management

- Never commit PAT to git
- Use environment variables
- Rotate tokens regularly
- Use minimal required permissions

### 2. Add to .gitignore

```bash
echo ".env" >> .gitignore
echo "*.token" >> .gitignore
```

### 3. Use GitHub Actions Secrets

For CI/CD, use GitHub Secrets instead of hardcoding tokens:

1. Go to repository Settings → Secrets and variables → Actions
2. Add new secret: `GHCR_TOKEN`
3. Use in workflows: `${{ secrets.GHCR_TOKEN }}`

## Quick Reference Commands

```bash
# Login
docker login ghcr.io -u USERNAME

# Tag
docker tag LOCAL_IMAGE:TAG ghcr.io/USERNAME/IMAGE:TAG

# Push
docker push ghcr.io/USERNAME/IMAGE:TAG

# Pull
docker pull ghcr.io/USERNAME/IMAGE:TAG

# Logout
docker logout ghcr.io

# View local images
docker images

# Remove image
docker rmi ghcr.io/USERNAME/IMAGE:TAG
```

## Next Steps

After successfully pushing to GHCR:

1. Test pulling the image on a different machine
2. Deploy to AWS EC2 (see AWS_DEPLOYMENT_GUIDE.md)
3. Set up automated builds with GitHub Actions
4. Configure monitoring (see MONITORING_GUIDE.md)

## Additional Resources

- [GHCR Documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Managing PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Docker Documentation](https://docs.docker.com/engine/reference/commandline/push/)
