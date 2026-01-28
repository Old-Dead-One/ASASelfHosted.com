# Email Verification Setup - TODO

## Issue

Users can sign up but don't receive verification emails because email service is not configured in Supabase.

## Impact

- Users see "Check your email" message but no email arrives
- Unverified users may be blocked by RLS policies
- Users get "Authentication required" errors when trying to use features

## Solution Options

### Option 1: Disable Email Verification (Development Only)

For local development, you can disable email verification in Supabase:

1. Go to Supabase Dashboard → Authentication → Settings
2. Under "Email Auth", disable "Enable email confirmations"
3. Users can sign up and immediately use the app

**⚠️ Warning:** Only do this in development. Production should require email verification.

### Option 2: Configure Email Service (Production)

For production, configure an email service in Supabase:

1. Go to Supabase Dashboard → Authentication → Email Templates
2. Configure SMTP settings:
   - Use a service like SendGrid, Mailgun, AWS SES, or Postmark
   - Add SMTP credentials to Supabase
3. Customize email templates if needed
4. Test email delivery

**Recommended Services:**
- **SendGrid**: Easy setup, good free tier
- **Mailgun**: Developer-friendly
- **AWS SES**: Cost-effective for high volume
- **Postmark**: Great deliverability

### Option 3: Manual Verification (Development Workaround)

For testing without email service:

1. Go to Supabase Dashboard → Authentication → Users
2. Find the unverified user
3. Click "..." menu → "Verify email"
4. User can now access features

## Current Status

- ✅ Frontend shows helpful messages about email verification
- ✅ TODO note added to signup confirmation page
- ⚠️ Email service not configured
- ⚠️ RLS may block unverified users (depends on Supabase settings)

## Next Steps

1. **For Development**: Disable email verification in Supabase Dashboard
2. **For Production**: Configure email service before launch
3. **Testing**: Use manual verification or disable requirement during development

## Related Files

- `frontend/src/pages/SignUpPage.tsx` - Shows email confirmation message with TODO
- `frontend/src/pages/DashboardPage.tsx` - Shows helpful error messages for unverified users
- `frontend/src/lib/api.ts` - Handles 401 errors with email verification context
