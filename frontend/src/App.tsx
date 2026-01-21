import { Layout } from './components/layout/Layout'
import { HomePage } from './pages/HomePage'

function App() {
    return (
        <Layout>
            {/* Route outlet goes here - replace HomePage with router when routing is added */}
            <HomePage />
        </Layout>
    )
}

export default App
