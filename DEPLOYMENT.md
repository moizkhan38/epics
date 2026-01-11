# Deployment Guide

This guide covers various deployment options for the Epics Generator API.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Cloud Deployment](#cloud-deployment)
3. [Manual Deployment](#manual-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Production Checklist](#production-checklist)

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Prepare environment file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with production values:
   ```env
   ENVIRONMENT=production
   DEBUG=False
   DATABASE_URL=postgresql+asyncpg://postgres:STRONG_PASSWORD@db:5432/epics_db
   ANTHROPIC_API_KEY=your-production-key
   API_KEYS=prod_key_1,prod_key_2
   SECRET_KEY=generate-a-strong-secret-key
   ```

2. **Build and start services**
   ```bash
   docker-compose up -d --build
   ```

3. **Run migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

4. **Verify deployment**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  db:
    image: ankane/pgvector:latest
    container_name: epics_db_prod
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: epics_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - epics_network

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: epics_api_prod
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/epics_db
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - API_KEYS=${API_KEYS}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
      - DEBUG=False
    ports:
      - "8000:8000"
    depends_on:
      - db
    restart: unless-stopped
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
      "
    networks:
      - epics_network

  nginx:
    image: nginx:alpine
    container_name: epics_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - epics_network

volumes:
  postgres_data:

networks:
  epics_network:
    driver: bridge
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS with RDS

1. **Create RDS PostgreSQL instance**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier epics-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --engine-version 15.3 \
     --master-username postgres \
     --master-user-password YOUR_PASSWORD \
     --allocated-storage 20
   ```

2. **Enable pgvector**
   Connect to RDS and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Build and push Docker image**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

   docker build -t epics-api .
   docker tag epics-api:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/epics-api:latest
   docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/epics-api:latest
   ```

4. **Create ECS task definition and service**
   Use AWS Console or CLI to create ECS resources with your Docker image.

5. **Configure environment variables**
   Set environment variables in ECS task definition:
   - DATABASE_URL
   - ANTHROPIC_API_KEY
   - API_KEYS
   - SECRET_KEY

#### Using AWS Lambda (Serverless)

Install Mangum for ASGI adapter:
```bash
pip install mangum
```

Modify `app/main.py`:
```python
from mangum import Mangum

# ... existing code ...

handler = Mangum(app)
```

Deploy using AWS SAM or Serverless Framework.

### Google Cloud Platform

#### Using Cloud Run

1. **Build container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/epics-api
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy epics-api \
     --image gcr.io/PROJECT_ID/epics-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL=$DATABASE_URL,ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
   ```

3. **Set up Cloud SQL PostgreSQL**
   Create Cloud SQL instance with PostgreSQL and enable pgvector.

### Azure Deployment

#### Using Azure Container Instances

1. **Create Azure Container Registry**
   ```bash
   az acr create --resource-group myResourceGroup --name epicsregistry --sku Basic
   ```

2. **Build and push image**
   ```bash
   az acr build --registry epicsregistry --image epics-api:latest .
   ```

3. **Deploy to Container Instances**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name epics-api \
     --image epicsregistry.azurecr.io/epics-api:latest \
     --dns-name-label epics-api \
     --ports 8000 \
     --environment-variables \
       DATABASE_URL=$DATABASE_URL \
       ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
   ```

### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   npm install -g heroku
   ```

2. **Create Heroku app**
   ```bash
   heroku create epics-api
   ```

3. **Add PostgreSQL addon**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set environment variables**
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your-key
   heroku config:set API_KEYS=your-api-keys
   heroku config:set SECRET_KEY=your-secret
   ```

5. **Create Procfile**
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   release: alembic upgrade head
   ```

6. **Deploy**
   ```bash
   git push heroku main
   ```

## Manual Deployment

### Ubuntu/Debian Server

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-15 nginx
   ```

2. **Install pgvector**
   ```bash
   cd /tmp
   git clone https://github.com/pgvector/pgvector.git
   cd pgvector
   make
   sudo make install
   ```

3. **Create database and enable pgvector**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE epics_db;
   \c epics_db
   CREATE EXTENSION vector;
   ```

4. **Set up application**
   ```bash
   cd /opt
   sudo git clone YOUR_REPO epics-api
   cd epics-api
   sudo python3.11 -m venv venv
   sudo venv/bin/pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   sudo nano .env
   # Add your configuration
   ```

6. **Create systemd service**
   ```bash
   sudo nano /etc/systemd/system/epics-api.service
   ```

   ```ini
   [Unit]
   Description=Epics Generator API
   After=network.target postgresql.service

   [Service]
   Type=notify
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/epics-api
   Environment="PATH=/opt/epics-api/venv/bin"
   ExecStart=/opt/epics-api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable epics-api
   sudo systemctl start epics-api
   ```

8. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/epics-api
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/epics-api /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

9. **Set up SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## Environment Configuration

### Production Environment Variables

```env
# Application
APP_NAME=Epics Generator API
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# Database (use strong password)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Security (generate strong keys)
API_KEYS=prod_key_1,prod_key_2,prod_key_3
SECRET_KEY=use-a-cryptographically-strong-secret-key

# Anthropic
ANTHROPIC_API_KEY=your-production-api-key
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
MAX_TOKENS=4096

# CORS (restrict to your domains)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_CREDENTIALS=True

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Generating Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate API keys
python -c "import secrets; print('api_' + secrets.token_urlsafe(32))"
```

## Production Checklist

### Security
- [ ] Use strong, unique API keys
- [ ] Generate cryptographically secure SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Restrict CORS to specific domains
- [ ] Enable rate limiting
- [ ] Review and restrict database permissions
- [ ] Keep dependencies updated

### Performance
- [ ] Enable database connection pooling
- [ ] Configure appropriate worker count (2-4 × CPU cores)
- [ ] Set up caching if needed
- [ ] Monitor response times
- [ ] Optimize database queries
- [ ] Create database indexes

### Reliability
- [ ] Set up automated backups
- [ ] Configure health checks
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation
- [ ] Enable auto-restart on failure
- [ ] Test disaster recovery procedures

### Monitoring
- [ ] Set up application monitoring (e.g., DataDog, New Relic)
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Monitor database performance
- [ ] Track API usage and costs
- [ ] Set up uptime monitoring

### Compliance
- [ ] Review data retention policies
- [ ] Ensure GDPR compliance if applicable
- [ ] Document API usage terms
- [ ] Set up audit logging
- [ ] Review security policies

## Maintenance

### Backup Database
```bash
pg_dump -h localhost -U postgres epics_db > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
psql -h localhost -U postgres epics_db < backup_20260111.sql
```

### Update Application
```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart epics-api
```

### Monitor Logs
```bash
# Application logs
sudo journalctl -u epics-api -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```
