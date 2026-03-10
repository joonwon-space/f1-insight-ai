import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { RootLayout } from '@/components/layout/RootLayout'
import { NewsPage } from '@/pages/NewsPage'
import { NewsDetailPage } from '@/pages/NewsDetailPage'
import { SchedulePage } from '@/pages/SchedulePage'
import { SearchPage } from '@/pages/SearchPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<RootLayout />}>
          <Route path="/" element={<NewsPage />} />
          <Route path="/news/:articleId" element={<NewsDetailPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/search" element={<SearchPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
