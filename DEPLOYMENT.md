# 🚀 Liara.ir Deployment Guide

This guide will help you deploy your Django personal site to Liara.ir.

## 🔧 Prerequisites

- Liara.ir account
- PostgreSQL database (provided by Liara.ir)
- Redis cache (optional, for better performance)

## 📋 Step-by-Step Deployment

### 1. Prepare Your Project

Make sure your project is ready for production:

```bash
# Install production dependencies
pip install -r requirements-liara.txt

# Collect static files
python manage.py collectstatic --noinput

# Create production settings
# (Already created: personal_site/settings_prod.py)
```

### 2. Environment Variables

Set these environment variables in Liara.ir dashboard:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.liara.ir,your-app.liara.ir

# Database (PostgreSQL)
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432

# Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Cache (Redis - optional)
REDIS_URL=redis://your-redis-host:6379/1

# Rate Limiting
CONTACT_RATE_LIMIT=3
CONTACT_RATE_LIMIT_WINDOW=300
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data
```

### 4. Liara.ir Configuration

#### A. Create New App
1. Go to [Liara.ir Dashboard](https://console.liara.ir)
2. Click "Create New App"
3. Choose "Web App"
4. Select Python runtime

#### B. Connect Repository
1. Connect your GitHub/GitLab repository
2. Set build command: `pip install -r requirements-liara.txt`
3. Set start command: `gunicorn personal_site.wsgi_liara:application --bind 0.0.0.0:$PORT`

#### C. Environment Variables
1. Go to "Environment Variables" section
2. Add all the environment variables listed above
3. Make sure `DEBUG=False` and `SECRET_KEY` is set

#### D. Database
1. Go to "Databases" section
2. Create PostgreSQL database
3. Copy connection details to environment variables

### 5. Build and Deploy

1. Push your changes to the connected repository
2. Liara.ir will automatically build and deploy
3. Monitor the build logs for any errors

## 🐛 Troubleshooting

### Logging Error (Fixed)
The original error was caused by Django trying to write to a file that doesn't exist in production. This is now fixed with:
- Production settings use console-only logging
- File logging only enabled in development
- Proper error handling for file operations

### Common Issues

#### Static Files Not Loading
```bash
# Make sure static files are collected
python manage.py collectstatic --noinput

# Check STATIC_ROOT in settings
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

#### Database Connection Issues
- Verify database credentials in environment variables
- Check if database is accessible from Liara.ir
- Ensure PostgreSQL is running

#### Import Errors
- Make sure all dependencies are in `requirements-liara.txt`
- Check if any development-only packages are being imported

## 🔒 Security Checklist

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` is set and secure
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] HTTPS is enabled
- [ ] Database credentials are secure
- [ ] Email credentials are secure

## 📊 Performance Optimization

### Database
- Use PostgreSQL (already configured)
- Consider database connection pooling

### Caching
- Redis for session and cache storage
- Django cache framework configured

### Static Files
- WhiteNoise for static file serving
- CDN for better global performance

## 🔄 Continuous Deployment

1. Connect your repository to Liara.ir
2. Set up automatic deployments on push
3. Configure staging and production environments
4. Set up monitoring and alerts

## 📞 Support

If you encounter issues:
1. Check Liara.ir build logs
2. Verify environment variables
3. Check Django error logs
4. Contact Liara.ir support

## 🎯 Next Steps

After successful deployment:
1. Set up custom domain
2. Configure SSL certificate
3. Set up monitoring and logging
4. Configure backup strategies
5. Set up CI/CD pipeline

---

**Happy Deploying! 🚀**
