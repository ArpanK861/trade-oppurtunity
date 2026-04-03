import { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function AuthWrapper({ children }) {
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const authenticate = async () => {
      try {
        const existingToken = localStorage.getItem('trade_jwt');
        if (existingToken) {
          // Token exists, assume it's valid for now. It'll throw 401 if expired.
          setIsAuthorized(true);
          return;
        }

        const response = await axios.post(`${API_URL}/auth/guest`);
        if (response.data && response.data.access_token) {
          localStorage.setItem('trade_jwt', response.data.access_token);
          setIsAuthorized(true);
        }
      } catch (err) {
        console.error("Authorization failed:", err);
        setError("Failed to connect to the backend. Is the server running?");
      }
    };

    authenticate();
  }, []);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500 font-medium">
        {error}
      </div>
    );
  }

  if (!isAuthorized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  return <>{children}</>;
}
