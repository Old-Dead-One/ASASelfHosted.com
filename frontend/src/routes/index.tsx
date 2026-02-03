/**
 * Route configuration.
 *
 * Defines all application routes.
 */

import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { HomePage } from '@/pages/HomePage'
import { ServerPage } from '@/pages/ServerPage'
import { LoginPage } from '@/pages/LoginPage'
import { SignUpPage } from '@/pages/SignUpPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { VerificationPage } from '@/pages/VerificationPage'
import { ConsentPage } from '@/pages/ConsentPage'
import { PrivacyPage } from '@/pages/PrivacyPage'
import { TermsPage } from '@/pages/TermsPage'
import { PrivacyPolicyPage } from '@/pages/PrivacyPolicyPage'
import { DataRightsPage } from '@/pages/DataRightsPage'
import { ContactPage } from '@/pages/ContactPage'
import { FaqPage } from '@/pages/FaqPage'
import { AboutPage } from '@/pages/AboutPage'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

export const router = createBrowserRouter([
    {
        path: '/',
        element: <Layout />,
        children: [
            {
                index: true,
                element: <HomePage />,
            },
            {
                path: 'servers/:serverId',
                element: <ServerPage />,
            },
            {
                path: 'login',
                element: <LoginPage />,
            },
            {
                path: 'signup',
                element: <SignUpPage />,
            },
            {
                path: 'forgot-password',
                element: <ForgotPasswordPage />,
            },
            {
                path: 'reset-password',
                element: <ResetPasswordPage />,
            },
            {
                path: 'dashboard',
                element: (
                    <ProtectedRoute>
                        <DashboardPage />
                    </ProtectedRoute>
                ),
            },
            {
                path: 'verification',
                element: <VerificationPage />,
            },
            {
                path: 'consent',
                element: <ConsentPage />,
            },
            {
                path: 'privacy',
                element: <PrivacyPage />,
            },
            {
                path: 'terms',
                element: <TermsPage />,
            },
            {
                path: 'privacy-policy',
                element: <PrivacyPolicyPage />,
            },
            {
                path: 'data-rights',
                element: <DataRightsPage />,
            },
            {
                path: 'contact',
                element: <ContactPage />,
            },
            {
                path: 'faq',
                element: <FaqPage />,
            },
            {
                path: 'about',
                element: <AboutPage />,
            },
            {
                path: '404',
                element: <NotFoundPage />,
            },
            {
                path: '*',
                element: <Navigate to="/404" replace />,
            },
        ],
    },
])
