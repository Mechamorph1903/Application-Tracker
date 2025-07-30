# 📧 Email Configuration for Render Deployment

## Required Environment Variables

Add these environment variables in your **Render Dashboard**:

### Gmail SMTP Settings
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=interninden@gmail.com
MAIL_PASSWORD=wafvxroqqfjoibmi
MAIL_DEFAULT_SENDER=interninden@gmail.com
```

### Supabase Settings (Already configured)
```
SUPABASE_URL=https://yzrfoxjwqlthhmwvqguu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DATABASE_URL=postgresql://postgres.yzrfoxjwqlthhmwvqguu...
SUPABASE_BUCKET=profile-pics
FORCE_SUPABASE=true
SECRET_KEY=98e3c291d7ae1b1abdd47f1e69a81e58037ed78f8bdb705680c4f24a42bcb147
```

## 🔧 Post-Deployment Setup

### 1. Test Email Functionality
After deployment, test these features:
- [ ] Password reset emails
- [ ] Welcome emails for new users
- [ ] Account migration emails

### 2. Update URLs in Email Templates
Replace `https://your-app-url.onrender.com` with your actual Render URL in:
- Welcome email template
- Password reset links
- Any other email templates

### 3. Email Security Best Practices
- [x] Using Gmail App Password (not regular password)
- [x] TLS encryption enabled
- [x] Environment variables secured in Render
- [x] Professional sender email address

## 📱 Integration Points

### Supabase Auth Integration
- Password reset emails work with Supabase Auth system
- User migration emails for existing users
- Account verification emails

### Application Features
- Welcome emails for new registrations
- Password reset via Supabase Auth
- Email notifications for friend requests (optional)
- Application deadline reminders (future feature)

## 🚨 Troubleshooting

### Common Issues:
1. **Email not sending**: Check Gmail App Password is correct
2. **TLS errors**: Ensure MAIL_USE_TLS=True and MAIL_USE_SSL=False
3. **Authentication errors**: Verify Gmail 2FA is enabled and App Password generated
4. **Template errors**: Check all email templates have correct variables

### Debug Commands:
```python
# In Flask shell
from app import create_app
app = create_app()
with app.app_context():
    print(f"Mail Server: {app.config['MAIL_SERVER']}")
    print(f"Mail Username: {app.config['MAIL_USERNAME']}")
```
