import { useState } from 'react';
import axios from 'axios';
import AuthWrapper from './components/AuthWrapper';
import FloatingBackground from './components/FloatingBackground';
import Hero from './components/Hero';
import LoadingState from './components/LoadingState';
import ReportViewer from './components/ReportViewer';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function TradeApp() {
  const [viewState, setViewState] = useState('idle'); // idle | loading | success
  const [reportData, setReportData] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async (sector) => {
    setViewState('loading');
    setError('');
    document.activeElement?.blur();

    const runAnalysis = async (tokenOverride = null) => {
      try {
        const token = tokenOverride || localStorage.getItem('trade_jwt');
        const response = await axios.get(`${API_URL}/analyze/${encodeURIComponent(sector.toLowerCase())}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        setReportData(response.data);
        setViewState('success');
      } catch (err) {
        // If the token is invalid/expired, transparently refresh and retry once
        if (err.response?.status === 401 && !tokenOverride) {
          try {
            const authRes = await axios.post(`${API_URL}/auth/guest`);
            const newToken = authRes.data.access_token;
            localStorage.setItem('trade_jwt', newToken);
            return await runAnalysis(newToken); // Retry the search
          } catch (authErr) {
            console.error("Token refresh failed", authErr);
            // Let it fall through to show error
          }
        }

        console.error(err);
        const msg = err.response?.data?.detail || err.message || "An unknown error occurred.";
        setError(msg);
        setViewState('idle'); // revert to idle to show error
      }
    };

    await runAnalysis();
  };

  const resetSearch = () => {
    setViewState('idle');
    setReportData(null);
    setError('');
  };

  return (
    <div className="relative min-h-screen text-slate-800 font-sans selection:bg-brand-blue/20">

      {/* Main Content Area */}
      <main className="relative z-10 pt-20 pb-10">
        {viewState === 'idle' && (
          <>
            <FloatingBackground />
            <Hero onAnalyze={handleAnalyze} />
            {error && (
              <div className="max-w-2xl mx-auto px-4 mt-8">
                <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm font-medium text-center">
                  ⚠️ {error}
                </div>
              </div>
            )}
          </>
        )}

        {viewState === 'loading' && <LoadingState />}
        
        {viewState === 'success' && <ReportViewer data={reportData} onReset={resetSearch} />}
        
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthWrapper>
      <TradeApp />
    </AuthWrapper>
  );
}
