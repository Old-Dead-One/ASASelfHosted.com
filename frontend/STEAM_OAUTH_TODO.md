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

Add Steam OAuth methods:

```typescript
const signInWithSteam = useCallback(async () => {
    if (isSupabaseConfigured() && supabase) {
        const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'steam',
            options: {
                redirectTo: `${window.location.origin}/auth/callback`,
            },
        })
        if (error) throw error
        // OAuth redirect happens automatically
    } else {
        // Dev mode: mock Steam login
        enableDevAuth('steam-user')
        // ... set mock user
    }
}, [])
```

#### 2.2 Create OAuth Callback Page (`src/pages/AuthCallbackPage.tsx`)

Handle OAuth redirect and extract session:

```typescript
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'

export function AuthCallbackPage() {
    const navigate = useNavigate()

    useEffect(() => {
        supabase?.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                // Successfully authenticated
                navigate('/dashboard', { replace: true })
            } else {
                // Auth failed
                navigate('/login?error=oauth_failed', { replace: true })
            }
        })
    }, [navigate])

    return <div>Completing authentication...</div>
}
```

#### 2.3 Update Login/SignUp Pages

Uncomment and implement Steam buttons:

- `src/pages/LoginPage.tsx` - Add `handleSteamLogin` function
- `src/pages/SignUpPage.tsx` - Add `handleSteamSignUp` function

#### 2.4 Add Route

Update `src/routes/index.tsx`:

```typescript
{
    path: 'auth/callback',
    element: <AuthCallbackPage />,
},
```

### 3. Backend Considerations

#### 3.1 User Metadata

Store Steam user ID in `user_metadata`:

```typescript
// After successful OAuth, user_metadata will contain:
// {
//   steam_id: "76561198012345678",
//   provider: "steam"
// }
```

#### 3.2 API Integration

- Backend can use `user_metadata.steam_id` for Steam-related features
- Consider adding Steam profile link to user profile
- May want to validate Steam ownership for server verification

### 4. UI/UX Enhancements

1. **Steam Button Styling:**
   - Use official Steam brand colors: `#1b2838` (dark blue)
   - Add Steam logo/icon
   - Match Steam's button style guidelines

2. **Error Handling:**
   - Handle OAuth cancellation gracefully
   - Show clear error messages for OAuth failures
   - Provide fallback to email/password

3. **Account Linking:**
   - Consider allowing users to link Steam account to existing email account
   - Show linked accounts in user settings

### 5. Testing

1. **Local Development:**
   - Test with Supabase local development
   - Mock Steam OAuth in dev mode

2. **Production:**
   - Test full OAuth flow
   - Verify redirect URLs work correctly
   - Test error scenarios (cancellation, network errors)

### 6. Documentation

- Update user documentation with Steam login instructions
- Document Steam API key setup process
- Add troubleshooting guide for common OAuth issues

## References

- [Supabase Auth - Social Login](https://supabase.com/docs/guides/auth/social-login)
- [Supabase Auth - Steam Provider](https://supabase.com/docs/guides/auth/social-login/auth-steam)
- [Steam Web API Documentation](https://steamcommunity.com/dev)
- [Steam Brand Guidelines](https://partner.steamgames.com/doc/store/branding)

## Notes

- Steam OAuth requires a valid Steam Web API key
- OAuth flow requires HTTPS in production
- Consider rate limiting for OAuth endpoints
- May want to add Steam profile picture/username display in user profile

## Current Status

- ✅ Placeholder UI added to LoginPage and SignUpPage (commented out)
- ✅ TODO comments in place
- ⏳ Supabase configuration pending
- ⏳ OAuth callback page pending
- ⏳ AuthContext methods pending
- ⏳ Route configuration pending
