# Complete Monitoring & Alerting Setup Guide

This guide provides step-by-step instructions to set up complete monitoring and observability with alerts sent to Email and Slack.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AWS EC2 Instance                         │
│                                                               │
│  ┌──────────────┐     ┌───────────────┐                     │
│  │ Sudoku Web   │────►│ Node Exporter │                     │
│  │ Application  │     │  (Port 9100)  │                     │
│  │ (Port 5000)  │     └───────┬───────┘                     │
│  └──────────────┘             │                              │
│                                │                              │
│                         ┌──────▼──────────┐                  │
│                         │   Prometheus    │                  │
│                         │   (Port 9090)   │                  │
│                         │   + Alert Rules │                  │
│                         └──────┬──────────┘                  │
│                                │                              │
│                    ┌───────────┴──────────┐                  │
│                    │                       │                  │
│             ┌──────▼────────┐    ┌────────▼────────┐        │
│             │  Alertmanager │    │     Grafana     │        │
│             │  (Port 9093)  │    │   (Port 3000)   │        │
│             └───────┬───────┘    └─────────────────┘        │
│                     │                                         │
└─────────────────────┼─────────────────────────────────────────┘
                      │
          ┌───────────┴──────────┐
          │                      │
    ┌─────▼─────┐        ┌──────▼──────┐
    │   Email   │        │    Slack    │
    │  Alerts   │        │   Alerts    │
    └───────────┘        └─────────────┘
```

## Prerequisites

- EC2 instance with monitoring stack (see MONITORING_GUIDE.md)
- Email account (Gmail recommended)
- Slack workspace with admin access

## Part 1: Install Alertmanager

### Step 1.1: Download and Install Alertmanager

SSH to your EC2 instance:

```bash
ssh -i "Sudoku-3X3.pem" ubuntu@YOUR_EC2_IP
```

Download Alertmanager:

```bash
# Create directory
cd ~/monitoring

# Download Alertmanager (check latest version at https://prometheus.io/download/)
wget https://github.com/prometheus/alertmanager/releases/download/v0.27.0/alertmanager-0.27.0.linux-amd64.tar.gz

# Extract
tar xvfz alertmanager-0.27.0.linux-amd64.tar.gz

# Copy binary
sudo cp alertmanager-0.27.0.linux-amd64/alertmanager /usr/local/bin/
sudo cp alertmanager-0.27.0.linux-amd64/amtool /usr/local/bin/

# Create directories
sudo mkdir -p /etc/alertmanager
sudo mkdir -p /var/lib/alertmanager

# Clean up
rm -rf alertmanager-0.27.0.linux-amd64*

# Verify installation
alertmanager --version
```

### Step 1.2: Create Alertmanager User

```bash
# Create user
sudo useradd --no-create-home --shell /bin/false alertmanager

# Set ownership
sudo chown -R alertmanager:alertmanager /etc/alertmanager
sudo chown -R alertmanager:alertmanager /var/lib/alertmanager
sudo chown alertmanager:alertmanager /usr/local/bin/alertmanager
sudo chown alertmanager:alertmanager /usr/local/bin/amtool
```

## Part 2: Configure Slack Integration

### Step 2.1: Create Slack Webhook

1. Go to your Slack workspace
2. Visit: https://api.slack.com/apps
3. Click **Create New App** → **From scratch**
4. App Name: `Prometheus Alerts`
5. Choose your workspace
6. Click **Create App**

7. In the app settings:
   - Click **Incoming Webhooks** (left sidebar)
   - Toggle **Activate Incoming Webhooks** to ON
   - Click **Add New Webhook to Workspace**
   - Select channel (e.g., #alerts or #monitoring)
   - Click **Allow**

8. **Copy the Webhook URL** - it looks like:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

### Step 2.2: Test Slack Webhook

Test from EC2:

```bash
# Test Slack webhook (replace with your URL)
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Hello from Prometheus Alertmanager! 🚀"}' \
https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

You should see a message in your Slack channel!

## Part 3: Configure Email (Gmail)

### Step 3.1: Set Up Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Enable **2-Step Verification** (if not already enabled)
4. Go back to Security
5. Click **App passwords**
6. Select app: **Mail**
7. Select device: **Other** (enter "Prometheus")
8. Click **Generate**
9. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

**Note**: Remove spaces when using: `abcdefghijklmnop`

### Step 3.2: Test Email Configuration

Create test script:

```bash
# Install mailutils (optional, for testing)
sudo apt-get install -y mailutils

# Or test with Python
python3 << 'EOF'
import smtplib
from email.mime.text import MIMEText

sender = 'your-email@gmail.com'
receiver = 'recipient@example.com'
app_password = 'abcdefghijklmnop'  # Your 16-char app password

msg = MIMEText('Test email from Prometheus Alertmanager')
msg['Subject'] = 'Test Alert'
msg['From'] = sender
msg['To'] = receiver

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(sender, app_password)
server.send_message(msg)
server.quit()
print('Email sent successfully!')
EOF
```

## Part 4: Configure Alertmanager

### Step 4.1: Create Alertmanager Configuration

Create config file:

```bash
sudo nano /etc/alertmanager/alertmanager.yml
```

Add the following configuration (replace with your details):

```yaml
# Alertmanager Configuration

global:
  # Global configuration
  resolve_timeout: 5m

  # Slack API URL
  slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'

  # SMTP (Email) configuration
  smtp_from: 'your-email@gmail.com'
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password-here'
  smtp_require_tls: true

# Template files (optional)
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route configuration
route:
  # Default receiver for all alerts
  receiver: 'default-receiver'

  # Group alerts by these labels
  group_by: ['alertname', 'cluster', 'service']

  # How long to wait before sending notification
  group_wait: 10s

  # How long to wait before sending notification about new alerts
  group_interval: 10s

  # How long to wait before re-sending notification
  repeat_interval: 3h

  # Child routes for specific alerts
  routes:
    # Critical alerts go to both Slack and Email immediately
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 10s
      repeat_interval: 5m

    # Warning alerts go to Slack only
    - match:
        severity: warning
      receiver: 'slack-warnings'
      group_wait: 30s
      repeat_interval: 1h

    # Info alerts
    - match:
        severity: info
      receiver: 'slack-info'
      group_wait: 1m
      repeat_interval: 4h

# Inhibit rules (prevent duplicate alerts)
inhibit_rules:
  # If critical alert is firing, don't send warning alerts
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'instance']

# Receivers configuration
receivers:
  # Default receiver (Slack + Email)
  - name: 'default-receiver'
    slack_configs:
      - channel: '#alerts'
        title: '🔔 Alert: {{ .GroupLabels.alertname }}'
        text: "{{ range .Alerts }}*Alert:* {{ .Annotations.summary }}\n*Details:* {{ .Annotations.description }}\n*Severity:* {{ .Labels.severity }}\n{{ end }}"
        send_resolved: true

    email_configs:
      - to: 'your-email@gmail.com'
        headers:
          Subject: '🔔 [{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
        html: |
          <h2>Alert Notification</h2>
          {{ range .Alerts }}
          <h3>{{ .Annotations.summary }}</h3>
          <p><strong>Description:</strong> {{ .Annotations.description }}</p>
          <p><strong>Severity:</strong> {{ .Labels.severity }}</p>
          <p><strong>Instance:</strong> {{ .Labels.instance }}</p>
          <p><strong>Started:</strong> {{ .StartsAt }}</p>
          {{ if .EndsAt }}<p><strong>Ended:</strong> {{ .EndsAt }}</p>{{ end }}
          <hr>
          {{ end }}
        send_resolved: true

  # Critical alerts (Slack + Email)
  - name: 'critical-alerts'
    slack_configs:
      - channel: '#alerts'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
        text: "{{ range .Alerts }}*Alert:* {{ .Annotations.summary }}\n*Details:* {{ .Annotations.description }}\n*Instance:* {{ .Labels.instance }}\n{{ end }}"
        color: danger
        send_resolved: true

    email_configs:
      - to: 'your-email@gmail.com, admin@example.com'
        headers:
          Subject: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
          Priority: 'urgent'
        html: |
          <div style="background-color: #ff0000; color: white; padding: 20px; border-radius: 5px;">
            <h2>🚨 CRITICAL ALERT</h2>
          </div>
          {{ range .Alerts }}
          <h3>{{ .Annotations.summary }}</h3>
          <p><strong>Description:</strong> {{ .Annotations.description }}</p>
          <p><strong>Severity:</strong> {{ .Labels.severity }}</p>
          <p><strong>Instance:</strong> {{ .Labels.instance }}</p>
          <p><strong>Started:</strong> {{ .StartsAt }}</p>
          {{ end }}
        send_resolved: true

  # Slack warnings only
  - name: 'slack-warnings'
    slack_configs:
      - channel: '#alerts'
        title: '⚠️ Warning: {{ .GroupLabels.alertname }}'
        text: "{{ range .Alerts }}{{ .Annotations.summary }}\n{{ .Annotations.description }}{{ end }}"
        color: warning
        send_resolved: true

  # Slack info only
  - name: 'slack-info'
    slack_configs:
      - channel: '#monitoring'
        title: 'ℹ️ Info: {{ .GroupLabels.alertname }}'
        text: "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"
        color: good
        send_resolved: true
```

**Replace these values:**
- `YOUR/WEBHOOK/URL` - Your Slack webhook URL
- `your-email@gmail.com` - Your Gmail address
- `your-app-password-here` - Your 16-character app password
- `admin@example.com` - Additional email recipients

Save and exit (Ctrl+X, Y, Enter)

### Step 4.2: Validate Configuration

```bash
# Check configuration syntax
amtool check-config /etc/alertmanager/alertmanager.yml

# Should output: "SUCCESS: /etc/alertmanager/alertmanager.yml is valid"
```

### Step 4.3: Create Systemd Service

```bash
sudo nano /etc/systemd/system/alertmanager.service
```

Add:

```ini
[Unit]
Description=Alertmanager
Documentation=https://prometheus.io/docs/alerting/alertmanager/
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=alertmanager
Group=alertmanager
ExecStart=/usr/local/bin/alertmanager \
    --config.file=/etc/alertmanager/alertmanager.yml \
    --storage.path=/var/lib/alertmanager/ \
    --web.listen-address=0.0.0.0:9093 \
    --cluster.advertise-address=0.0.0.0:9093

SyslogIdentifier=alertmanager
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save and exit

### Step 4.4: Start Alertmanager

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Alertmanager
sudo systemctl start alertmanager

# Enable auto-start
sudo systemctl enable alertmanager

# Check status
sudo systemctl status alertmanager

# Check logs
sudo journalctl -u alertmanager -f
```

### Step 4.5: Verify Alertmanager

```bash
# Test locally
curl http://localhost:9093

# Check API
curl http://localhost:9093/api/v2/status
```

Access web UI:
```
http://YOUR_EC2_IP:9093
```

## Part 5: Create Alert Rules for Prometheus

### Step 5.1: Create Alert Rules File

```bash
sudo nano /etc/prometheus/alert_rules.yml
```

Add comprehensive alert rules:

```yaml
groups:
  # System Health Alerts
  - name: system_health
    interval: 30s
    rules:
      # Instance down
      - alert: InstanceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Instance {{ $labels.instance }} is down"
          description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 1 minute."

      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% (current value: {{ $value }}%)"

      # Critical CPU usage
      - alert: CriticalCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 95% (current value: {{ $value }}%)"

  # Memory Alerts
  - name: memory_alerts
    interval: 30s
    rules:
      # High memory usage
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 80% (current value: {{ $value }}%)"

      # Critical memory usage
      - alert: CriticalMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: Memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 90% (current value: {{ $value }}%)"

  # Disk Alerts
  - name: disk_alerts
    interval: 30s
    rules:
      # Low disk space
      - alert: LowDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk space is below 20% (current value: {{ $value }}%)"

      # Critical disk space
      - alert: CriticalDiskSpace
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: Disk space on {{ $labels.instance }}"
          description: "Disk space is below 10% (current value: {{ $value }}%)"

      # High disk I/O
      - alert: HighDiskIO
        expr: rate(node_disk_io_time_seconds_total[5m]) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High disk I/O on {{ $labels.instance }}"
          description: "Disk I/O is high (current value: {{ $value }})"

  # Application Alerts
  - name: application_alerts
    interval: 30s
    rules:
      # Sudoku application down
      - alert: SudokuAppDown
        expr: up{job="sudoku-game"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Sudoku application is down"
          description: "The Sudoku web application on {{ $labels.instance }} is not responding"

      # High response time
      - alert: HighResponseTime
        expr: http_request_duration_seconds > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time for {{ $labels.instance }}"
          description: "HTTP response time is above 1 second"

  # Docker Container Alerts
  - name: docker_alerts
    interval: 30s
    rules:
      # Container down
      - alert: ContainerDown
        expr: up{job="cadvisor"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Docker container is down"
          description: "Container {{ $labels.instance }} is not running"

      # High container CPU
      - alert: HighContainerCPU
        expr: rate(container_cpu_usage_seconds_total{name="sudoku-game"}[5m]) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage in container"
          description: "Container CPU usage is above 80%"

      # High container memory
      - alert: HighContainerMemory
        expr: (container_memory_usage_bytes{name="sudoku-game"} / container_spec_memory_limit_bytes{name="sudoku-game"}) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage in container"
          description: "Container memory usage is above 80%"

  # Network Alerts
  - name: network_alerts
    interval: 30s
    rules:
      # High network traffic
      - alert: HighNetworkTraffic
        expr: rate(node_network_receive_bytes_total[5m]) > 100000000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High network traffic on {{ $labels.instance }}"
          description: "Network receiving > 100MB/s"

      # High network errors
      - alert: HighNetworkErrors
        expr: rate(node_network_receive_errs_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High network errors on {{ $labels.instance }}"
          description: "Network errors detected"
```

Save and exit

### Step 5.2: Update Prometheus Configuration

```bash
sudo nano /etc/prometheus/prometheus.yml
```

Add Alertmanager configuration:

```yaml
# Add this to the existing prometheus.yml

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - localhost:9093

# Rule files
rule_files:
  - "alert_rules.yml"
```

### Step 5.3: Validate and Reload Prometheus

```bash
# Validate Prometheus config
sudo promtool check config /etc/prometheus/prometheus.yml

# Validate alert rules
sudo promtool check rules /etc/prometheus/alert_rules.yml

# Reload Prometheus (or restart)
sudo systemctl reload prometheus
# OR
sudo systemctl restart prometheus

# Check status
sudo systemctl status prometheus
```

## Part 6: Configure Grafana Alerts

### Step 6.1: Access Grafana

Open browser:
```
http://YOUR_EC2_IP:3000
```

Login: `admin` / `your-password`

### Step 6.2: Add Alertmanager as Data Source

1. Click **Configuration** (gear icon) → **Data sources**
2. Click **Add data source**
3. Select **Alertmanager**
4. Configure:
   - **Name**: Alertmanager
   - **URL**: `http://localhost:9093`
5. Click **Save & Test**

### Step 6.3: Configure Notification Channels

#### Slack Notification:

1. Go to **Alerting** (bell icon) → **Contact points**
2. Click **+ New contact point**
3. Configure:
   - **Name**: Slack Alerts
   - **Type**: Slack
   - **Webhook URL**: Your Slack webhook URL
   - **Title**: `{{ .GroupLabels.alertname }}`
   - **Text**: `{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}`
4. Click **Test** to verify
5. Click **Save contact point**

#### Email Notification:

1. Click **+ New contact point**
2. Configure:
   - **Name**: Email Alerts
   - **Type**: Email
   - **Addresses**: `your-email@gmail.com`
3. Click **Save contact point**

### Step 6.4: Create Alert Rules in Grafana

1. Go to **Alerting** → **Alert rules**
2. Click **+ New alert rule**
3. Configure alert for high CPU:
   - **Alert name**: High CPU Alert
   - **Query**: Select Prometheus
   - **Metric**: `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
   - **Condition**: IS ABOVE 80
   - **For**: 5m
4. Add contact point: Select **Slack Alerts** or **Email Alerts**
5. Click **Save**

## Part 7: Update AWS Security Group

Add Alertmanager port to security group:

1. AWS Console → EC2 → Security Groups
2. Select your security group
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 9093
   - Source: My IP (for security)

## Part 8: Test Alerts

### Test 8.1: Trigger CPU Alert

```bash
# Install stress tool
sudo apt-get install -y stress

# Generate CPU load for 6 minutes (triggers alert after 5 min)
stress --cpu 4 --timeout 360s
```

You should receive alerts in Slack and Email!

### Test 8.2: Send Test Alert via API

```bash
# Send test alert to Alertmanager
curl -X POST http://localhost:9093/api/v2/alerts \
  -H 'Content-Type: application/json' \
  -d '[
    {
      "labels": {
        "alertname": "TestAlert",
        "severity": "warning",
        "instance": "test-instance"
      },
      "annotations": {
        "summary": "This is a test alert",
        "description": "Testing alert system"
      }
    }
  ]'
```

### Test 8.3: Check Alert Status

```bash
# View active alerts in Prometheus
curl http://localhost:9090/api/v1/alerts

# View alerts in Alertmanager
curl http://localhost:9093/api/v2/alerts

# Check Alertmanager status
amtool --alertmanager.url=http://localhost:9093 alert
```

## Part 9: Monitoring Dashboard URLs

After setup, access these dashboards:

| Service | URL | Description |
|---------|-----|-------------|
| Sudoku Game | http://YOUR_IP:5000 | Web application |
| Prometheus | http://YOUR_IP:9090 | Metrics & alerts |
| Alertmanager | http://YOUR_IP:9093 | Alert management |
| Grafana | http://YOUR_IP:3000 | Dashboards |
| Node Exporter | http://YOUR_IP:9100/metrics | System metrics |

## Part 10: Troubleshooting

### Alerts not sending to Slack

```bash
# Check Alertmanager logs
sudo journalctl -u alertmanager -f

# Test webhook manually
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test from Alertmanager"}' \
YOUR_SLACK_WEBHOOK_URL

# Verify Alertmanager config
amtool check-config /etc/alertmanager/alertmanager.yml
```

### Email alerts not working

```bash
# Check if port 587 is accessible
telnet smtp.gmail.com 587

# Verify app password is correct
# Re-generate if needed

# Check Alertmanager logs for SMTP errors
sudo journalctl -u alertmanager -n 100 | grep -i smtp
```

### Prometheus not loading rules

```bash
# Check rule syntax
sudo promtool check rules /etc/prometheus/alert_rules.yml

# Restart Prometheus
sudo systemctl restart prometheus

# View alerts in Prometheus UI
# Go to http://YOUR_IP:9090/alerts
```

## Quick Reference Commands

```bash
# Service management
sudo systemctl status alertmanager
sudo systemctl status prometheus
sudo systemctl status grafana-server

# Logs
sudo journalctl -u alertmanager -f
sudo journalctl -u prometheus -f

# Config validation
amtool check-config /etc/alertmanager/alertmanager.yml
promtool check config /etc/prometheus/prometheus.yml
promtool check rules /etc/prometheus/alert_rules.yml

# View alerts
amtool --alertmanager.url=http://localhost:9093 alert
curl http://localhost:9090/api/v1/alerts
```

## Best Practices

1. **Alert Fatigue**: Don't create too many alerts
2. **Severity Levels**: Use critical/warning/info appropriately
3. **Group Alerts**: Group related alerts to reduce noise
4. **Test Regularly**: Test alert channels monthly
5. **Document**: Keep runbooks for common alerts
6. **Silence**: Use Alertmanager silence feature during maintenance
7. **Review**: Review and tune alert thresholds regularly

## Next Steps

1. Create custom Grafana dashboards
2. Set up log aggregation (Loki)
3. Add application-specific metrics
4. Configure PagerDuty for on-call
5. Implement automated remediation

## Additional Resources

- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [Slack API](https://api.slack.com/messaging/webhooks)
