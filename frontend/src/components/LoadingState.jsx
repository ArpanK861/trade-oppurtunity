import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const LOADING_STATUSES = [
  "Initializing Analysis Engine...",
  "Fetching NSE & BSE Market Data...",
  "Cross-referencing global sentiment...",
  "Synthesizing insights..."
];

export default function LoadingState() {
  const [statusIndex, setStatusIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStatusIndex((prev) => Math.min(prev + 1, LOADING_STATUSES.length - 1));
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8 select-none relative z-50 pointer-events-auto">
      {/* Pulse Circle */}
      <div className="relative flex items-center justify-center">
        <motion.div
          animate={{
            scale: [1, 2.5, 1],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute w-24 h-24 rounded-full bg-brand-blue/30"
        />
        <motion.div
          animate={{
            scale: [1, 1.8, 1],
            opacity: [0.8, 0, 0.8],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 0.3,
            ease: "easeInOut",
          }}
          className="absolute w-16 h-16 rounded-full bg-brand-blue/50"
        />
        <div className="relative w-12 h-12 rounded-full bg-brand-blue shadow-[0_0_20px_rgba(59,130,246,0.6)] flex items-center justify-center">
          <div className="w-4 h-4 bg-white rounded-full mx-auto" />
        </div>
      </div>

      {/* Typing Text */}
      <div className="flex flex-col items-center space-y-2">
        <motion.p
          key={statusIndex}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          className="text-lg font-medium text-slate-700 tracking-tight"
        >
          {LOADING_STATUSES[statusIndex]}
        </motion.p>
        <p className="text-sm text-slate-400 font-medium tracking-wide">
          Please wait while the report is generated
        </p>
      </div>
    </div>
  );
}
