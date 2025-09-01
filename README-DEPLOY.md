# StudyBuddyBot Deployment Guide

This guide explains how to deploy the StudyBuddyBot to both development and production environments using the deployment script.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or higher)
- Git

## Configuration

The bot uses different configurations for development and production environments:

### Development Environment (`bot_test`)
- **Bot Name**: Тестовый бот
- **Bot Link**: https://t.me/TestPhystechBot
- **Token**: 7547512356:AAE_4pkglMhbyw_Qg3n2w3wQB2gkAvnlDZc
- **Purpose**: Testing and development

### Production Environment (`bot`)
- **Bot Name**: Навигатор Бизнес-школы МФТИ
- **Bot Link**: https://t.me/fbvt_bot
- **Token**: 8399290351:AAH6djaO1ALpzU_YWF0eT0ZCg509rm-6R_s
- **Purpose**: Live production bot

## Quick Start

### Deploy to Production
```bash
./deploy.sh deploy prod
```

### Deploy to Development
```bash
./deploy.sh deploy dev
```

## Deployment Script Commands

The `deploy.sh` script provides comprehensive deployment management:

| Command | Description | Example |
|---------|-------------|---------|
| `deploy` | Deploy the application | `./deploy.sh deploy prod` |
| `build` | Build the application image | `./deploy.sh build dev` |
| `start` | Start the application | `./deploy.sh start prod` |
| `stop` | Stop the application | `./deploy.sh stop dev` |
| `restart` | Restart the application | `./deploy.sh restart prod` |
| `logs` | Show application logs | `./deploy.sh logs dev` |
| `status` | Show deployment status | `./deploy.sh status prod` |
| `clean` | Clean up deployment artifacts | `./deploy.sh clean dev` |
| `help` | Show help message | `./deploy.sh help` |

## Environment-Specific Features

### Production Environment (`prod`)
- **Docker Compose File**: `docker-compose.prod.yml`
- **Dockerfile**: `Dockerfile.prod`
- **Bot Configuration**: Uses `bot` config from `config.yaml`
- **Container Name**: `studybuddibot-prod`
- **Image Tag**: `studybuddibot:prod`
- **Features**:
  - Optimized for production
  - Health checks enabled
  - Non-root user for security
  - Minimal system dependencies
  - Restart policy: `unless-stopped`

### Development Environment (`dev`)
- **Docker Compose File**: `docker-compose.dev.yml`
- **Dockerfile**: `Dockerfile.dev`
- **Bot Configuration**: Uses `bot_test` config from `config.yaml`
- **Container Name**: `studybuddibot-dev`
- **Image Tag**: `studybuddibot:dev`
- **Features**:
  - Hot reloading enabled
  - Development tools included
  - Debug mode enabled
  - Source code mounted for live editing

## Deployment Process

### 1. Configuration Check
The deployment script automatically checks for required files:
- `config.yaml` - Bot configuration
- `requirements.txt` - Python dependencies
- `bot.py` - Main application file

### 2. Environment Selection
The script uses the `BOT_CONFIG` environment variable to select the appropriate bot configuration:
- `prod` environment → `BOT_CONFIG=bot` (production bot)
- `dev` environment → `BOT_CONFIG=bot_test` (development bot)

### 3. Docker Build
- Builds optimized Docker images for each environment
- Uses environment-specific Dockerfiles
- Includes all necessary dependencies

### 4. Service Deployment
- Starts Redis service for data storage
- Deploys the bot application
- Sets up networking between services
- Configures health checks and restart policies

## Service Architecture

### Production Services
```
studybuddibot-prod (Bot Application)
├── Redis:6380 (Data Storage)
└── Health Checks
```

### Development Services
```
studybuddibot-dev (Bot Application)
├── Redis:6379 (Data Storage)
├── Bot Web Interface:8001 (Optional)
├── Redis Commander:8081 (Optional)
└── Hot Reloading
```

## Monitoring and Management

### View Logs
```bash
# Production logs
./deploy.sh logs prod

# Development logs
./deploy.sh logs dev
```

### Check Status
```bash
# Production status
./deploy.sh status prod

# Development status
./deploy.sh status dev
```

### Restart Services
```bash
# Restart production
./deploy.sh restart prod

# Restart development
./deploy.sh restart dev
```

## Cleanup

### Remove Deployment
```bash
# Clean up production
./deploy.sh clean prod

# Clean up development
./deploy.sh clean dev
```

This will:
- Stop all containers
- Remove containers, networks, and volumes
- Delete Docker images
- Clean up all deployment artifacts

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Start Docker Desktop or Docker daemon
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop on macOS/Windows
   ```

2. **Port conflicts**
   - Production uses port 6380 for Redis
   - Development uses ports 6379 (Redis), 8001 (Bot), and 8081 (Redis Commander)
   - Ensure these ports are available

3. **Permission issues**
   ```bash
   # Make script executable
   chmod +x deploy.sh
   ```

4. **Configuration errors**
   - Check that `config.yaml` contains valid bot configurations
   - Ensure all required environment variables are set

### Debug Mode

For detailed debugging, you can run the deployment script with verbose output:
```bash
# Enable bash debugging
bash -x ./deploy.sh deploy prod
```

## Security Considerations

### Production Deployment
- Uses non-root user in containers
- Minimal system dependencies
- Health checks for monitoring
- Restart policies for reliability
- Isolated network configuration

### Development Deployment
- Includes development tools
- Debug mode enabled
- Source code mounted for live editing
- Optional Redis Commander for database management

## Backup and Recovery

### Data Backup
Redis data is persisted in Docker volumes:
- Production: `redis_data_prod`
- Development: `redis_data`

### Recovery Process
1. Stop the current deployment
2. Restore Redis data from backup
3. Redeploy using the deployment script

## Support

For deployment issues:
1. Check the logs: `./deploy.sh logs [env]`
2. Verify configuration: `./deploy.sh status [env]`
3. Clean and redeploy: `./deploy.sh clean [env] && ./deploy.sh deploy [env]`
