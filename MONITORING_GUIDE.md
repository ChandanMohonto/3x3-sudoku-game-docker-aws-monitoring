# Complete Monitoring Setup Guide

This guide provides detailed steps to set up comprehensive monitoring for your Sudoku game using Node Exporter, Prometheus, and Grafana on AWS EC2.

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    EC2 Instance                          │
│                                                           │
│  ┌──────────────┐    ┌───────────────┐                  │
│  │  Sudoku Game │    │ Node Exporter │                  │
│  │  Container   │    │   (Port 9100) │                  │
│  │ (Port 8080)  │    └───────┬───────┘                  │
│  └──────────────┘            │                           │
│                               │                           │
│                        ┌──────▼──────┐                   │
│                        │ Prometheus  │                   │
│                        │ (Port 9090) │                   │
│                        └──────┬──────┘                   │
│                               │                           │
│                        ┌──────▼──────┐                   │
│                        │   Grafana   │                   │
│                        │ (Port 3000) │                   │
│                        └─────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- EC2 instance running (see AWS_DEPLOYMENT_GUIDE.md)
- SSH access to EC2 instance
- Security group configured with required ports
- Docker installed on EC2

## Part 1: Install Node Exporter

Node Exporter collects hardware and OS metrics from your EC2 instance.

### Step 1.1: Download Node Exporter

SSH into your EC2 instance:

```bash
ssh -i "sudoku-game-key.pem" ec2-user@YOUR_INSTANCE_PUBLIC_IP
```

Download and install Node Exporter:

```bash
# Create directory for monitoring tools
mkdir -p ~/monitoring
cd ~/monitoring

# Download Node Exporter (check for latest version at https://prometheus.io/download/)
wget https://github.com/prometheus/node_exporter/releases/download/v1.7.0/node_exporter-1.7.0.linux-amd64.tar.gz

# Extract the archive
tar xvfz node_exporter-1.7.0.linux-amd64.tar.gz

# Move to /usr/local/bin
sudo cp node_exporter-1.7.0.linux-amd64/node_exporter /usr/local/bin/

# Clean up
rm -rf node_exporter-1.7.0.linux-amd64*

# Verify installation
node_exporter --version
```

### Step 1.2: Create Node Exporter User

Create a dedicated user for security:

```bash
# Create user
sudo useradd --no-create-home --shell /bin/false node_exporter

# Set ownership
sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
```

### Step 1.3: Create Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/node_exporter.service
```

Add the following content:

```ini
[Unit]
Description=Node Exporter
Documentation=https://prometheus.io/docs/guides/node-exporter/
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=node_exporter
Group=node_exporter
ExecStart=/usr/local/bin/node_exporter \
    --collector.filesystem.mount-points-exclude=^/(dev|proc|sys|var/lib/docker/.+|var/lib/kubelet/.+)($|/) \
    --collector.netclass.ignored-devices=^(veth.*)$ \
    --collector.cpu \
    --collector.meminfo \
    --collector.diskstats \
    --collector.filesystem \
    --collector.netdev \
    --collector.netstat \
    --collector.vmstat

SyslogIdentifier=node_exporter
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, Y, Enter)

### Step 1.4: Start Node Exporter

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Node Exporter
sudo systemctl start node_exporter

# Enable auto-start on boot
sudo systemctl enable node_exporter

# Check status
sudo systemctl status node_exporter
```

Expected output:

```
● node_exporter.service - Node Exporter
   Loaded: loaded (/etc/systemd/system/node_exporter.service; enabled)
   Active: active (running)
```

### Step 1.5: Verify Node Exporter

```bash
# Check if Node Exporter is responding
curl http://localhost:9100/metrics
```

You should see metrics output like:

```
# HELP node_cpu_seconds_total Seconds the CPUs spent in each mode.
# TYPE node_cpu_seconds_total counter
node_cpu_seconds_total{cpu="0",mode="idle"} 12345.67
...
```

## Part 2: Install and Configure Prometheus

Prometheus scrapes and stores metrics from Node Exporter and other sources.

### Step 2.1: Download Prometheus

```bash
cd ~/monitoring

# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz

# Extract
tar xvfz prometheus-2.48.0.linux-amd64.tar.gz

# Create directories
sudo mkdir -p /etc/prometheus
sudo mkdir -p /var/lib/prometheus

# Copy binaries
sudo cp prometheus-2.48.0.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-2.48.0.linux-amd64/promtool /usr/local/bin/

# Copy console files
sudo cp -r prometheus-2.48.0.linux-amd64/consoles /etc/prometheus
sudo cp -r prometheus-2.48.0.linux-amd64/console_libraries /etc/prometheus

# Clean up
rm -rf prometheus-2.48.0.linux-amd64*

# Verify installation
prometheus --version
```

### Step 2.2: Create Prometheus User

```bash
# Create user
sudo useradd --no-create-home --shell /bin/false prometheus

# Set ownership
sudo chown -R prometheus:prometheus /etc/prometheus
sudo chown -R prometheus:prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /usr/local/bin/prometheus
sudo chown prometheus:prometheus /usr/local/bin/promtool
```

### Step 2.3: Configure Prometheus

Create configuration file:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add the following configuration:

```yaml
# Prometheus Configuration File

global:
  scrape_interval: 15s           # How frequently to scrape targets
  evaluation_interval: 15s       # How frequently to evaluate rules
  scrape_timeout: 10s           # Timeout for scraping
  external_labels:
    cluster: 'sudoku-game'
    environment: 'production'

# Alertmanager configuration (optional)
# alerting:
#   alertmanagers:
#     - static_configs:
#         - targets: ['localhost:9093']

# Rule files (for alerting rules)
rule_files:
  # - "alert_rules.yml"

# Scrape configurations
scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        labels:
          instance: 'prometheus-server'

  # Node Exporter - System metrics
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
        labels:
          instance: 'ec2-sudoku-server'
          service: 'node-exporter'

  # Docker Container Metrics (cAdvisor)
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:8080']
        labels:
          instance: 'sudoku-game-container'
    metrics_path: '/metrics'

  # Sudoku Game Application (if exposing metrics)
  - job_name: 'sudoku-game'
    static_configs:
      - targets: ['localhost:8080']
        labels:
          app: 'sudoku-game'
          version: '1.0'
```

Save and exit (Ctrl+X, Y, Enter)

Verify configuration syntax:

```bash
sudo promtool check config /etc/prometheus/prometheus.yml
```

### Step 2.4: Create Prometheus Systemd Service

```bash
sudo nano /etc/systemd/system/prometheus.service
```

Add the following:

```ini
[Unit]
Description=Prometheus
Documentation=https://prometheus.io/docs/introduction/overview/
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --storage.tsdb.retention.time=15d \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:9090 \
    --web.enable-lifecycle

SyslogIdentifier=prometheus
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save and exit

### Step 2.5: Start Prometheus

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Prometheus
sudo systemctl start prometheus

# Enable auto-start
sudo systemctl enable prometheus

# Check status
sudo systemctl status prometheus
```

### Step 2.6: Verify Prometheus

Check if Prometheus is running:

```bash
# Test locally
curl http://localhost:9090

# Check targets
curl http://localhost:9090/api/v1/targets
```

Access Prometheus web UI:
- From browser: `http://YOUR_EC2_PUBLIC_IP:9090`
- Check Status → Targets to see if all targets are "UP"

## Part 3: Install and Configure Grafana

Grafana provides beautiful dashboards for visualizing Prometheus data.

### Step 3.1: Install Grafana

**For Amazon Linux 2023**:

```bash
# Create Grafana YUM repository
sudo tee /etc/yum.repos.d/grafana.repo <<EOF
[grafana]
name=grafana
baseurl=https://rpm.grafana.com
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://rpm.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF

# Install Grafana
sudo yum install grafana -y
```

**For Ubuntu**:

```bash
# Install prerequisites
sudo apt-get install -y software-properties-common

# Add Grafana GPG key
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

# Add repository
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Update and install
sudo apt-get update
sudo apt-get install grafana -y
```

### Step 3.2: Start Grafana

```bash
# Start Grafana
sudo systemctl start grafana-server

# Enable auto-start
sudo systemctl enable grafana-server

# Check status
sudo systemctl status grafana-server
```

### Step 3.3: Access Grafana

Open browser and navigate to:

```
http://YOUR_EC2_PUBLIC_IP:3000
```

**Default credentials**:
- Username: `admin`
- Password: `admin`

You'll be prompted to change the password on first login.

## Part 4: Configure Grafana Dashboards

### Step 4.1: Add Prometheus Data Source

1. Login to Grafana (http://YOUR_EC2_PUBLIC_IP:3000)
2. Click on **Configuration** (gear icon) → **Data sources**
3. Click **Add data source**
4. Select **Prometheus**
5. Configure:
   - **Name**: Prometheus
   - **URL**: `http://localhost:9090`
   - **Access**: Server (default)
6. Click **Save & Test**

You should see: "Data source is working"

### Step 4.2: Import Node Exporter Dashboard

1. Click **Dashboards** (four squares icon) → **Import**
2. Enter Dashboard ID: `1860` (Node Exporter Full)
3. Click **Load**
4. Configure:
   - **Name**: Node Exporter Full
   - **Prometheus**: Select "Prometheus" (from dropdown)
5. Click **Import**

You should now see a complete dashboard with:
- CPU usage
- Memory usage
- Disk I/O
- Network traffic
- System load
- And more!

### Step 4.3: Create Custom Dashboard for Docker Metrics

1. Click **Create** (+) → **Dashboard**
2. Click **Add new panel**
3. Add queries:

**Panel 1: Container CPU Usage**
```promql
rate(container_cpu_usage_seconds_total{name="sudoku-game"}[5m]) * 100
```

**Panel 2: Container Memory Usage**
```promql
container_memory_usage_bytes{name="sudoku-game"} / 1024 / 1024
```

**Panel 3: Container Network I/O**
```promql
rate(container_network_receive_bytes_total{name="sudoku-game"}[5m])
```

4. Save dashboard as "Sudoku Game Monitoring"

### Step 4.4: Import Pre-built Dashboards

Import these popular dashboards:

| Dashboard | ID | Description |
|-----------|-----|-------------|
| Node Exporter Full | 1860 | Complete system metrics |
| Docker Monitoring | 193 | Docker container metrics |
| Prometheus 2.0 Stats | 3662 | Prometheus performance |
| System Overview | 11074 | High-level system view |

To import:
1. Go to Dashboards → Import
2. Enter dashboard ID
3. Click Load
4. Select Prometheus data source
5. Click Import

## Part 5: Set Up cAdvisor for Docker Metrics

cAdvisor provides detailed container metrics.

### Step 5.1: Run cAdvisor Container

```bash
# Run cAdvisor
docker run -d \
  --name=cadvisor \
  --restart=unless-stopped \
  -p 8081:8080 \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --privileged \
  --device=/dev/kmsg \
  gcr.io/cadvisor/cadvisor:latest
```

### Step 5.2: Update Prometheus Configuration

Edit Prometheus config:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add cAdvisor scrape config:

```yaml
  # cAdvisor - Docker container metrics
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8081']
        labels:
          instance: 'cadvisor'
```

Reload Prometheus:

```bash
sudo systemctl reload prometheus
# or send SIGHUP
sudo killall -HUP prometheus
```

### Step 5.3: Verify cAdvisor

Access cAdvisor web UI:

```
http://YOUR_EC2_PUBLIC_IP:8081
```

Check metrics:

```bash
curl http://localhost:8081/metrics
```

## Part 6: Configure Alerts (Optional)

### Step 6.1: Create Alert Rules

Create alerts file:

```bash
sudo nano /etc/prometheus/alert_rules.yml
```

Add alert rules:

```yaml
groups:
  - name: system_alerts
    interval: 30s
    rules:
      # High CPU usage alert
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% on {{ $labels.instance }}"

      # High memory usage alert
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% on {{ $labels.instance }}"

      # Disk space alert
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space is below 15% on {{ $labels.instance }}"

      # Container down alert
      - alert: ContainerDown
        expr: up{job="docker"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Container is down"
          description: "Sudoku game container is not responding"

      # High network traffic
      - alert: HighNetworkTraffic
        expr: rate(node_network_receive_bytes_total[5m]) > 50000000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High network traffic"
          description: "Network receiving > 50MB/s on {{ $labels.instance }}"
```

Update Prometheus config to include rules:

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Update rule_files section:

```yaml
rule_files:
  - "alert_rules.yml"
```

Restart Prometheus:

```bash
sudo systemctl restart prometheus
```

View alerts in Prometheus UI:
- Navigate to `http://YOUR_EC2_PUBLIC_IP:9090/alerts`

## Part 7: Complete Docker Compose Setup

For easier management, use Docker Compose:

### Step 7.1: Create Docker Compose File

```bash
cd ~/monitoring
nano docker-compose-monitoring.yml
```

Add:

```yaml
version: '3.8'

services:
  # Sudoku Game
  sudoku-game:
    image: ghcr.io/YOUR_GITHUB_USERNAME/sudoku-game:latest
    container_name: sudoku-game
    ports:
      - "8080:8080"
    restart: unless-stopped
    stdin_open: true
    tty: true
    networks:
      - monitoring

  # cAdvisor
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
      - "8081:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    restart: unless-stopped
    networks:
      - monitoring

  # Node Exporter (alternative to systemd service)
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.rootfs=/host'
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped
    networks:
      - monitoring

networks:
  monitoring:
    driver: bridge
```

### Step 7.2: Run with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose-monitoring.yml up -d

# View logs
docker-compose -f docker-compose-monitoring.yml logs -f

# Stop all services
docker-compose -f docker-compose-monitoring.yml down
```

## Part 8: Monitoring Best Practices

### Step 8.1: Regular Maintenance

Create maintenance script:

```bash
nano ~/monitoring-maintenance.sh
```

Add:

```bash
#!/bin/bash

echo "=== Monitoring System Maintenance ==="
echo ""

echo "1. Checking service status..."
sudo systemctl status node_exporter --no-pager
sudo systemctl status prometheus --no-pager
sudo systemctl status grafana-server --no-pager

echo ""
echo "2. Checking disk usage..."
df -h /var/lib/prometheus

echo ""
echo "3. Prometheus data retention..."
du -sh /var/lib/prometheus/*

echo ""
echo "4. Docker container status..."
docker ps | grep -E "cadvisor|sudoku-game"

echo ""
echo "5. Recent log entries..."
sudo journalctl -u prometheus -n 10 --no-pager

echo ""
echo "Maintenance check complete!"
```

Make executable:

```bash
chmod +x ~/monitoring-maintenance.sh
./monitoring-maintenance.sh
```

### Step 8.2: Set Up Log Rotation

For Prometheus logs:

```bash
sudo nano /etc/logrotate.d/prometheus
```

Add:

```
/var/log/prometheus/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 prometheus prometheus
    postrotate
        systemctl reload prometheus > /dev/null 2>&1 || true
    endscript
}
```

## Troubleshooting

### Node Exporter Issues

**Not starting**:

```bash
# Check logs
sudo journalctl -u node_exporter -n 50 --no-pager

# Check if port is in use
sudo netstat -tulpn | grep 9100

# Restart service
sudo systemctl restart node_exporter
```

### Prometheus Issues

**Targets down**:

```bash
# Check Prometheus logs
sudo journalctl -u prometheus -n 50 --no-pager

# Verify configuration
sudo promtool check config /etc/prometheus/prometheus.yml

# Test target connectivity
curl http://localhost:9100/metrics
```

**Storage issues**:

```bash
# Check disk space
df -h /var/lib/prometheus

# Clean old data (reduces retention)
sudo systemctl stop prometheus
sudo rm -rf /var/lib/prometheus/data/*
sudo systemctl start prometheus
```

### Grafana Issues

**Can't access UI**:

```bash
# Check service status
sudo systemctl status grafana-server

# Check logs
sudo journalctl -u grafana-server -n 50 --no-pager

# Check if port is available
sudo netstat -tulpn | grep 3000

# Restart Grafana
sudo systemctl restart grafana-server
```

**Data source not working**:
- Verify Prometheus URL: `http://localhost:9090`
- Check firewall rules
- Test Prometheus API: `curl http://localhost:9090/api/v1/status/config`

### cAdvisor Issues

**Container not starting**:

```bash
# Check logs
docker logs cadvisor

# Restart container
docker restart cadvisor

# Remove and recreate
docker rm -f cadvisor
# Then run the docker run command again
```

## Performance Tuning

### Optimize Prometheus

Edit `/etc/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 30s      # Increase for lower load
  scrape_timeout: 10s
  evaluation_interval: 30s

# Reduce retention time
# In systemd service file: --storage.tsdb.retention.time=7d
```

### Optimize Grafana

Edit `/etc/grafana/grafana.ini`:

```ini
[server]
# Reduce protocol
protocol = http

[database]
# Use SQLite for small deployments (default)

[security]
# Disable registration
allow_sign_up = false
```

## Quick Reference

### Service Management

```bash
# Node Exporter
sudo systemctl start|stop|restart|status node_exporter

# Prometheus
sudo systemctl start|stop|restart|status prometheus

# Grafana
sudo systemctl start|stop|restart|status grafana-server

# Docker containers
docker start|stop|restart cadvisor
```

### Access URLs

| Service | URL | Default Port |
|---------|-----|--------------|
| Grafana | http://YOUR_IP:3000 | 3000 |
| Prometheus | http://YOUR_IP:9090 | 9090 |
| Node Exporter | http://YOUR_IP:9100/metrics | 9100 |
| cAdvisor | http://YOUR_IP:8081 | 8081 |

### Important Files

```bash
# Prometheus
/etc/prometheus/prometheus.yml
/etc/prometheus/alert_rules.yml
/var/lib/prometheus/

# Grafana
/etc/grafana/grafana.ini
/var/lib/grafana/

# Logs
/var/log/prometheus/
/var/log/grafana/
```

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Node Exporter Guide](https://prometheus.io/docs/guides/node-exporter/)
- [cAdvisor Documentation](https://github.com/google/cadvisor)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

## Next Steps

1. Set up alerting with Alertmanager
2. Configure email/Slack notifications
3. Create custom dashboards
4. Implement log aggregation (ELK/Loki)
5. Set up automated backups
6. Configure SSL/TLS for secure access
