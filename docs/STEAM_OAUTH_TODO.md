# Steam OAuth Integration - TODO (Post-Sprint 6)

## Overview

Add Steam OAuth login/signup to the authentication flow. This allows users to authenticate using their Steam account instead of (or in addition to) email/password.

## Implementation Steps

### 1. Supabase Configuration

1. **Enable Steam OAuth in Supabase Dashboard:**
   - Go to Authentication → Providers → Steam
   - Enable Steam provider
   - Configure Steam API credentials:
     - Steam Web API Key (from https://steamcommunity.com/dev/apikey)
     - Redirect URL: `https://your-project.supabase.co/auth/v1/callback`

2. **Update Supabase Auth Settings:**
   - Ensure OAuth redirect URLs are configured correctly
   - Set allowed redirect URLs in Supabase Dashboard

### 2. Frontend Implementation

#### 2.1 Update AuthContext (`src/contexts/AuthContext.tsx`)

Add Steam OAuth methods (signInWithSteam, redirectTo, handle callback).

#### 2.2 Create OAuth Callback Page (`src/pages/AuthCallbackPage.tsx`)

Handle OAuth redirect and extract session; navigate to dashboard or login on failure.

#### 2.3 Update Login/SignUp Pages

Uncomment and implement Steam buttons in `LoginPage.tsx` and `SignUpPage.tsx`.

#### 2.4 Add Route

Add `auth/callback` route in `src/routes/index.tsx`.

### 3. Backend Considerations

- Store Steam user ID in `user_metadata`; backend can use for Steam-related features.
- Consider Steam profile link and validation for server verification.

### 4. UI/UX and Testing

- Steam button styling (brand colors, logo); error handling; account linking optional.
- Test local (mock) and production OAuth flow.

## References

- [Supabase Auth - Social Login](https://supabase.com/docs/guides/auth/social-login)
- [Supabase Auth - Steam Provider](https://supabase.com/docs/guides/auth/social-login/auth-steam)
- [Steam Web API](https://steamcommunity.com/dev)

## Current Status

- Placeholder UI and TODO comments in LoginPage and SignUpPage.
- Supabase config, callback page, AuthContext methods, and route pending.

When implementing, add to Sprint 8 or current sprint backlog and reference this doc.
