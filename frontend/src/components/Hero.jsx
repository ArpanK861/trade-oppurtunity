import { useState } from 'react';
import { Search, ArrowRight, Sparkles } from 'lucide-react';
import { Button } from "./ui/button";

export default function Hero({ onAnalyze, isLoading }) {
  const [sector, setSector] = useState('');
  const handleSubmit = (e) => {
    e.preventDefault();
    if (sector.trim()) {
      onAnalyze(sector);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4 text-center">
      <div id="hero-area" className="max-w-3xl w-full flex flex-col gap-6 lg:gap-8 relative z-10 py-10 px-6 pointer-events-auto">

        {/* Title */}
        <div className="flex flex-col items-center gap-4">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tighter leading-[1.1] text-slate-900">
            <span className="bg-gradient-to-r from-[#6ec3f4] to-[#3B82F6] bg-clip-text text-transparent px-2">
              Trade
            </span>
            Opportunity
          </h1>
          <p className="text-base text-slate-500 max-w-lg mx-auto font-medium">
            Analyze Indian market sectors instantly. Powered by Groq AI.
          </p>
        </div>

        {/* Search Component */}
        <div className="mx-auto max-w-xl w-full">
          <form
            onSubmit={handleSubmit}
            className="relative flex items-center w-full p-2 bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-200/60 focus-within:ring-4 focus-within:ring-brand-blue/10 transition-all duration-300"
          >
            <div className="pl-4 text-slate-400">
              <Search className="w-5 h-5" />
            </div>

            <input
              type="text"
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              placeholder="Search all sectors (e.g. pharmaceuticals, steel)"
              className="w-full px-4 py-4 text-lg bg-transparent border-none outline-none text-slate-800 placeholder:text-slate-400 font-medium disabled:opacity-50 disabled:bg-transparent"
              disabled={isLoading}
              required
            />

            <Button
              variant="outline"
              size="lg"
              type="submit"
              disabled={isLoading || !sector.trim()}
              className="absolute right-1 text-slate-700 hover:bg-slate-50 border-slate-200 shadow-none font-semibold transition-all"
            >
              {isLoading ? 'Analyzing...' : 'Analyze'}
              {!isLoading && (
                <Sparkles className="-me-1 ms-2 opacity-60" size={16} strokeWidth={2} aria-hidden="true" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}