# Deployment Guide - NL2SQL Churn POC

## 🚀 Quick Deployment

### Current Status
✅ **DEPLOYED AND RUNNING**

- **Live URL:** https://8000-iiobg734ojo79m1l1mgnq-225270a7.manusvm.computer
- **Port:** 8000
- **Status:** Active

### Accessing the Application

Simply open your browser and navigate to:
```
https://8000-iiobg734ojo79m1l1mgnq-225270a7.manusvm.computer
```

---

## 🔧 Manual Deployment

If you need to restart or redeploy the application:

### 1. Navigate to Project Directory
```bash
cd /home/ubuntu/nl2sql_churn_poc
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Start the Web Server
```bash
cd webapp
python app.py
```

The server will start on `http://0.0.0.0:8000`

### 4. Access the Application
- **Local:** http://localhost:8000
- **Public:** Use the exposed URL from the expose tool

---

## 🛠️ Troubleshooting

### Server Not Starting

**Problem:** Port already in use
```bash
# Check what's using port 8000
netstat -tuln | grep 8000

# Kill existing process
pkill -f "python app.py"

# Restart server
cd /home/ubuntu/nl2sql_churn_poc/webapp
source ../venv/bin/activate
python app.py
```

**Problem:** Module not found errors
```bash
# Reinstall dependencies
cd /home/ubuntu/nl2sql_churn_poc
source venv/bin/activate
pip install -r requirements.txt
```

### ChromaDB Issues

**Problem:** ChromaDB collection errors
```bash
# Delete and recreate ChromaDB
rm -rf /home/ubuntu/nl2sql_churn_poc/data/chromadb

# Re-run metadata ingestion
cd /home/ubuntu/nl2sql_churn_poc/src
source ../venv/bin/activate
python metadata_ingestion.py
```

### Azure OpenAI Connection Issues

**Problem:** API key errors or quota exceeded

1. Check credentials in `src/config.py`
2. Verify API key is valid
3. Check Azure OpenAI quota and limits
4. Ensure endpoint URL is correct

### Database Issues

**Problem:** Database locked or corrupted
```bash
# Regenerate database
cd /home/ubuntu/nl2sql_churn_poc
source venv/bin/activate
python generate_churn_data.py
```

---

## 📊 Monitoring

### Check Server Status
```bash
# Check if server is running
ps aux | grep "python app.py"

# Check server logs
tail -f /home/ubuntu/nl2sql_churn_poc/data/server.log
```

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "chromadb": "connected"
}
```

---

## 🔐 Security Considerations

### For Production Deployment

1. **Environment Variables**
   - Move API keys to environment variables
   - Use secrets management service
   - Never commit credentials to version control

2. **Authentication**
   - Add user authentication
   - Implement role-based access control
   - Use OAuth2 or JWT tokens

3. **HTTPS**
   - Use SSL/TLS certificates
   - Enforce HTTPS only
   - Configure proper CORS policies

4. **Rate Limiting**
   - Implement API rate limiting
   - Add request throttling
   - Monitor for abuse

5. **Input Validation**
   - Sanitize user inputs
   - Validate SQL queries
   - Prevent SQL injection

---

## 📦 Backup and Recovery

### Backup Database
```bash
# Backup SQLite database
cp /home/ubuntu/nl2sql_churn_poc/data/churn.db \
   /home/ubuntu/nl2sql_churn_poc/data/churn.db.backup

# Backup CSV files
tar -czf /home/ubuntu/nl2sql_churn_poc/data/csv_backup.tar.gz \
   /home/ubuntu/nl2sql_churn_poc/data/*.csv
```

### Backup Metadata
```bash
# Backup metadata files
tar -czf /home/ubuntu/nl2sql_churn_poc/metadata_backup.tar.gz \
   /home/ubuntu/nl2sql_churn_poc/metadata/
```

### Restore from Backup
```bash
# Restore database
cp /home/ubuntu/nl2sql_churn_poc/data/churn.db.backup \
   /home/ubuntu/nl2sql_churn_poc/data/churn.db

# Restore metadata
tar -xzf /home/ubuntu/nl2sql_churn_poc/metadata_backup.tar.gz \
   -C /home/ubuntu/nl2sql_churn_poc/
```

---

## 🔄 Updates and Maintenance

### Update Metadata
```bash
# After modifying metadata JSON files
cd /home/ubuntu/nl2sql_churn_poc/src
source ../venv/bin/activate
python metadata_ingestion.py
```

### Update Dependencies
```bash
cd /home/ubuntu/nl2sql_churn_poc
source venv/bin/activate
pip install --upgrade semantic-kernel chromadb fastapi
```

### Regenerate Data
```bash
cd /home/ubuntu/nl2sql_churn_poc
source venv/bin/activate
python generate_churn_data.py
```

---

## 🌐 Production Deployment Options

### Option 1: Docker Container

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "webapp/app.py"]
```

Build and run:
```bash
docker build -t nl2sql-churn-poc .
docker run -p 8000:8000 nl2sql-churn-poc
```

### Option 2: Cloud Deployment

**Azure App Service:**
```bash
az webapp up --name nl2sql-churn-poc --runtime "PYTHON:3.11"
```

**AWS Elastic Beanstalk:**
```bash
eb init -p python-3.11 nl2sql-churn-poc
eb create nl2sql-churn-poc-env
eb deploy
```

**Google Cloud Run:**
```bash
gcloud run deploy nl2sql-churn-poc \
  --source . \
  --platform managed \
  --region us-central1
```

### Option 3: Virtual Private Server

1. **Setup server** (Ubuntu 22.04)
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv nginx
   ```
3. **Clone project**
4. **Configure Nginx** as reverse proxy
5. **Use systemd** for process management
6. **Setup SSL** with Let's Encrypt

---

## 📈 Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use shared database (PostgreSQL instead of SQLite)
- Implement Redis for caching
- Use managed ChromaDB service

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize ChromaDB settings
- Add database indexes
- Implement query result caching

### Performance Optimization
- Cache ChromaDB search results
- Implement query result caching
- Use connection pooling
- Add CDN for static assets
- Compress responses

---

## 🧪 Testing Deployment

### Automated Health Check
```bash
#!/bin/bash
# health_check.sh

URL="http://localhost:8000/health"
RESPONSE=$(curl -s $URL)

if [[ $RESPONSE == *"healthy"* ]]; then
    echo "✅ Service is healthy"
    exit 0
else
    echo "❌ Service is unhealthy"
    exit 1
fi
```

### Load Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Run load test
ab -n 1000 -c 10 http://localhost:8000/
```

---

## 📝 Deployment Checklist

Before deploying to production:

- [ ] Update Azure OpenAI credentials
- [ ] Configure environment variables
- [ ] Set up HTTPS/SSL
- [ ] Implement authentication
- [ ] Add rate limiting
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Create backup strategy
- [ ] Test error handling
- [ ] Document API endpoints
- [ ] Perform security audit
- [ ] Load test the application
- [ ] Set up CI/CD pipeline
- [ ] Configure auto-scaling
- [ ] Implement health checks

---

## 🆘 Support

### Common Issues

1. **Slow query response**
   - Check Azure OpenAI quota
   - Optimize ChromaDB search
   - Add result caching

2. **High memory usage**
   - Reduce ChromaDB collection size
   - Implement pagination
   - Clear unused connections

3. **Database locked**
   - Use connection pooling
   - Consider PostgreSQL for production
   - Implement retry logic

### Getting Help

1. Check logs: `tail -f data/server.log`
2. Review error messages
3. Verify configuration in `src/config.py`
4. Test individual components
5. Check Azure OpenAI service status

---

## ✅ Current Deployment Status

**Environment:** Development/POC  
**Status:** ✅ Running  
**URL:** https://8000-iiobg734ojo79m1l1mgnq-225270a7.manusvm.computer  
**Database:** SQLite (4.2 MB)  
**Vector Store:** ChromaDB (local)  
**Server:** FastAPI + Uvicorn  
**Port:** 8000  

**Ready for:** Testing, demonstration, development  
**Not ready for:** Production deployment without security hardening  

---

*Last Updated: December 6, 2024*
