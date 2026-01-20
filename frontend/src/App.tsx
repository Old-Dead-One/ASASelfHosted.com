import { QueryClientProvider } from '@tanstack/react-query'
import { Layout } from './components/layout/Layout'
import { HomePage } from './pages/HomePage'
import { queryClient } from './lib/query-client'

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <Layout>
                <HomePage />
            </Layout>
        </QueryClientProvider>
    )
}

export default App
