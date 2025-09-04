# StudyBuddyBot Development Setup

This guide explains how to set up and run the StudyBuddyBot in development mode using Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or higher)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or higher)
- Git

## Remote Development

Since your computer and the remote PC (where Docker is running) are on the same network, you can access the services using the remote PC's local IP address:

- **Bot**: `http://REMOTE_PC_IP:8000` (if web interface is added)
- **Redis**: `REMOTE_PC_IP:6379`
- **Redis Commander**: `http://REMOTE_PC_IP:8081`

To find the remote PC's IP address:
```bash
# On the remote PC (Linux/Mac)
ip addr show

# On the remote PC (Windows)
ipconfig

# Or use hostname to get IP
hostname -I  # Linux
```

## Quick Start

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd StudyBuddyBot
   ```

2. **Start the development environment**:
   ```bash
   ./dev.sh start
   ```

3. **View logs**:
   ```bash
   ./dev.sh logs
   ```

4. **Access the bot container**:
   ```bash
   ./dev.sh shell
   ```

## Development Script Commands

The `dev.sh` script provides easy commands for managing the development environment:

| Command | Description |
|---------|-------------|
| `./dev.sh start` | Start the development environment |
| `./dev.sh stop` | Stop the development environment |
| `./dev.sh restart` | Restart the development environment |
| `./dev.sh logs` | Show logs from all services |
| `./dev.sh logs-bot` | Show logs from bot service only |
| `./dev.sh logs-redis` | Show logs from Redis service only |
| `./dev.sh shell` | Open shell in bot container |
| `./dev.sh redis-cli` | Open Redis CLI |
| `./dev.sh redis-ui` | Start Redis Commander (web UI) |
| `./dev.sh flush-db` | Flush all Redis databases |
| `./dev.sh build` | Rebuild the bot container |
| `./dev.sh clean` | Stop and remove all containers, networks, and volumes |
| `./dev.sh status` | Show status of all services |
| `./dev.sh help` | Show help message |

## Services

The development environment includes the following services:

### 1. Bot Service (`studybuddybot-dev`)
- **Image**: Built from `Dockerfile.dev`
- **Port**: 8000 (for potential web interface)
- **Volumes**:
  - `.:/app` - Source code for hot reloading
  - `./logs:/app/logs` - Log files
  - `./media:/app/media` - User media files

### 2. Redis Service (`studybuddybot-redis-dev`)
- **Image**: `redis:8.2-alpine`
- **Port**: 6379
- **Volumes**: `redis_data:/data` - Persistent Redis data
- **Features**: AOF persistence, health checks

### 3. Redis Commander (Optional)
- **Image**: `rediscommander/redis-commander:latest`
- **Port**: 8081
- **Access**: Port 8081 (use your remote PC's IP if accessing from another machine)
- **Start**: `./dev.sh redis-ui`



## Environment Variables

The following environment variables are automatically set in the development environment:

### Bot Configuration
- `BOT_TOKEN` - Telegram bot token
- `BOT_ID` - Telegram bot ID
- `BOT_NAME` - Bot name

### OpenAI Configuration
- `OPENAI_API_KEY` - OpenAI API key

### Redis Configuration
- `REDIS_HOST` - Redis host (set to `redis`)
- `REDIS_PORT` - Redis port (6379)
- `LANGGRAPH_REDIS_URL` - LangGraph Redis URL

### System Configuration
- `TIME_ZONE` - System timezone (Europe/Moscow)
- `DEBUG` - Debug mode (true)
- `DEVELOPMENT` - Development mode (true)

## Database Management

### Automatic Database Flushing
In development mode, the bot automatically flushes all Redis databases on startup. This ensures a clean state for each development session.

**When it happens:**
- Every time you start the bot with `./dev.sh start`
- Every time you restart the bot with `./dev.sh restart`
- Only when `DEVELOPMENT=true` environment variable is set

**What gets flushed:**
- All Redis databases (0, 1, 2, 3)
- FSM storage
- User data
- Temporary data

### Manual Database Flushing
You can manually flush the database at any time:

```bash
# Flush all Redis databases
./dev.sh flush-db
```

This command will prompt for confirmation before flushing.

## Development Workflow

### 1. Starting Development
```bash
# Start all services
./dev.sh start

# View logs
./dev.sh logs
```

### 2. Making Code Changes
Since the source code is mounted as a volume, most changes will be reflected immediately. However, for some changes (like new dependencies), you may need to restart the bot:

```bash
# Restart the bot service
./dev.sh restart
```

### 3. Accessing the Bot Container
```bash
# Open shell in bot container
./dev.sh shell

# Inside the container, you can:
python bot.py  # Run the bot manually
python -m pytest  # Run tests
black .  # Format code
flake8 .  # Lint code
```

### 4. Working with Redis
```bash
# Access Redis CLI
./dev.sh redis-cli

# Start Redis Commander (web UI)
./dev.sh redis-ui
# Then open http://localhost:8081 in your browser
```

### 5. Viewing Logs
```bash
# All services
./dev.sh logs

# Bot service only
./dev.sh logs-bot

# Redis service only
./dev.sh logs-redis
```

## File Structure

```
StudyBuddyBot/
├── docker-compose.dev.yml    # Development Docker Compose configuration
├── Dockerfile.dev           # Development Dockerfile
├── dev.sh                   # Development management script
├── bot.py                   # Main bot entry point
├── config.yaml              # Bot configuration
├── requirements.txt         # Python dependencies
├── src/                     # Source code
├── logs/                    # Log files (created automatically)
└── media/                   # User media files (created automatically)
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :6379
   lsof -i :8000
   
   # Stop conflicting services or change ports in docker-compose.dev.yml
   ```

2. **Container won't start**
   ```bash
   # Check container logs
   ./dev.sh logs
   
   # Rebuild container
   ./dev.sh build
   ```

3. **Redis connection issues**
   ```bash
   # Check Redis status
   ./dev.sh status
   
   # Test Redis connection
   ./dev.sh redis-cli
   ```

4. **Permission issues**
   ```bash
   # Make sure dev.sh is executable
   chmod +x dev.sh
   ```

### Cleaning Up

If you encounter persistent issues, you can clean everything and start fresh:

```bash
# Stop and remove everything
./dev.sh clean

# Start fresh
./dev.sh start
```

## Production vs Development

### Development Features
- Hot reloading of source code
- Development tools (pytest, black, flake8, mypy)
- Debug mode enabled
- Redis Commander for database management
- Detailed logging

### Production Differences
- Uses `Dockerfile` instead of `Dockerfile.dev`
- No development tools
- Optimized for performance
- Minimal logging
- No Redis Commander

## Contributing

When contributing to the project:

1. Use the development environment for testing
2. Run tests before submitting: `./dev.sh shell` then `python -m pytest`
3. Format code: `./dev.sh shell` then `black .`
4. Check linting: `./dev.sh shell` then `flake8 .`

## Support

If you encounter issues with the development setup:

1. Check the troubleshooting section above
2. Review the logs: `./dev.sh logs`
3. Ensure Docker and Docker Compose are properly installed
4. Try cleaning and restarting: `./dev.sh clean && ./dev.sh start`
