# Streamlit Cloud Deployment Guide

## Pre-deployment Checklist

✅ All issues from audit have been fixed
✅ Dependencies are properly specified in requirements.txt
✅ Environment variables are configured
✅ Database initialization is handled
✅ File upload limits are set
✅ Caching is implemented for performance

## Deployment Steps

### 1. Repository Setup
- Ensure your code is pushed to GitHub
- Make sure all files are committed
- Verify the repository is public or you have Streamlit Cloud access

### 2. Streamlit Cloud Configuration
1. Go to https://share.streamlit.io/
2. Connect your GitHub account
3. Select your repository
4. Set the main file path: `app.py`
5. Set the Python version: `3.9` or `3.10`

### 3. Configure Secrets
1. In your Streamlit Cloud app settings, go to "Secrets"
2. Copy the contents from `streamlit_secrets_template.toml`
3. Replace placeholder values with your actual API keys:
   - `PERPLEXITY_API_KEY`: Your Perplexity API key
   - `RAZORPAY_KEY_SECRET`: Your Razorpay secret key
   - `SECRET_KEY`: A random secret key for sessions
   - `RAZORPAY_KEY_ID`: Your Razorpay key ID

### 4. Monitor Deployment
- Check the deployment logs for any errors
- Test all functionality after deployment
- Monitor resource usage and performance

## Common Issues and Solutions

### Database Issues
- SQLite database will be recreated on each deployment
- User data will be lost unless using external database
- Consider upgrading to PostgreSQL for production

### Memory Issues
- Streamlit Cloud has memory limits
- Large file uploads may cause issues
- Session state cleanup is implemented to prevent memory leaks

### API Rate Limits
- Monitor API usage to avoid rate limits
- Implement proper error handling for API failures
- Consider caching API responses

### File Upload Issues
- File upload size is limited to 10MB
- Temporary files are cleaned up automatically
- Large files may cause timeout issues

## Performance Optimization

### Implemented Optimizations
- Session state cleanup to prevent memory leaks
- File upload size limits
- Caching for expensive operations
- Proper error handling

### Additional Recommendations
- Monitor app performance regularly
- Optimize database queries
- Use appropriate caching strategies
- Minimize session state usage

## Support and Troubleshooting

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all secrets are configured correctly
3. Test locally first
4. Check API key validity
5. Monitor resource usage

## Security Considerations

- Never commit API keys to the repository
- Use Streamlit Cloud secrets for sensitive data
- Implement proper input validation
- Monitor for suspicious activity
- Keep dependencies updated

## Post-Deployment

After successful deployment:
1. Test all features thoroughly
2. Monitor performance and errors
3. Set up monitoring and alerts
4. Plan for scaling if needed
5. Regular maintenance and updates
