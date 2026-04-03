import ReactMarkdown from 'react-markdown';
import { ArrowLeft, Clock, Server } from 'lucide-react';

export default function ReportViewer({ data, onReset }) {
  if (!data) return null;

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-200">
        <button
          onClick={onReset}
          className="flex items-center text-sm font-medium text-slate-500 hover:text-brand-blue transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 mr-2 transition-transform group-hover:-translate-x-1" />
          Back to Search
        </button>

        <div className="flex items-center space-x-4 text-xs font-semibold text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-100">
          <div className="flex items-center">
            <Clock className="w-3.5 h-3.5 mr-1" />
            {new Date(data.generated_at).toLocaleTimeString()}
          </div>
          <div className="w-px h-3 bg-slate-300" />
          <div className="flex items-center">
            <Server className="w-3.5 h-3.5 mr-1" />
            {data.model_used || 'AI Synthesized'}
          </div>
        </div>
      </div>

      {/* Markdown Content inside Prose */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8 sm:p-12">
        <article className="prose prose-slate prose-headings:font-bold prose-headings:tracking-tight prose-a:text-brand-blue hover:prose-a:underline prose-li:marker:text-brand-blue max-w-none">
          <ReactMarkdown>
            {data.report}
          </ReactMarkdown>
        </article>
      </div>
    </div>
  );
}
