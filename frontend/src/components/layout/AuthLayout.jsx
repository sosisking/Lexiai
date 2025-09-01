import { Link } from 'react-router-dom';
import { ThemeToggle } from '@/components/ThemeToggle';

export function AuthLayout({ children }) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex h-14 items-center px-4 lg:px-6 border-b bg-background">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
            <span className="text-lg font-bold text-primary-foreground">L</span>
          </div>
          <span className="text-xl font-bold">LexiAI</span>
        </Link>
        <div className="ml-auto flex items-center gap-2">
          <ThemeToggle />
        </div>
      </header>
      <main className="flex-1 flex items-center justify-center p-4 md:p-8 lg:p-12">
        <div className="mx-auto grid w-full max-w-md gap-6">
          {children}
        </div>
      </main>
      <footer className="border-t bg-background py-4 text-center text-sm text-muted-foreground">
        <div className="container mx-auto px-4">
          <p>© {new Date().getFullYear()} LexiAI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

