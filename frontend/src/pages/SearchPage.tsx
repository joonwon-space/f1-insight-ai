import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Search } from 'lucide-react'

export function SearchPage() {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Search</h1>
      <div className="flex max-w-lg gap-2">
        <Input placeholder="Search F1 news..." className="flex-1" />
        <Button>
          <Search className="mr-2 h-4 w-4" />
          Search
        </Button>
      </div>
    </div>
  )
}
