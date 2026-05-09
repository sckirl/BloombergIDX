'use client';

import React, { useEffect, useState, useCallback } from 'react';

// --- Types ---
interface InsiderTransaction {
  id: number;
  date: string;
  ticker: string;
  insider_name: string;
  role: string;
  transaction_type: string;
  shares: string | number;
  price: string | number;
  value: string | number;
  score: number;
  score_reasons?: string; 
  rvol?: number;
}

interface Signal {
  id: number;
  ticker: string;
  title: string;
  body: string;
  severity: 'HIGH' | 'MED' | 'LOW';
  timestamp: string;
}

// --- Components ---

const Sidebar = ({ onNav }: { onNav: (view: string) => void }) => (
  <aside className="w-[200px] border-r border-border-custom bg-black flex flex-col">
    <div className="p-4 border-b border-border-custom flex items-center gap-2">
      <div className="w-5 h-5 bg-acc rounded-sm"></div>
      <span className="font-bold text-xs tracking-tighter">IDX INSIDER</span>
    </div>
    <nav className="flex-1 p-2 space-y-1">
      {[
        { id: 'INSIDER', label: 'INSIDER FEED', cmd: 'INSIDER' },
        { id: 'FLOW', label: 'SMART FLOW', cmd: 'FLOW' },
        { id: 'ANOMALY', label: 'ANOMALIES', cmd: 'ANOMALY' },
        { id: 'HEATMAP', label: 'HEATMAP', cmd: 'MAP' },
        { id: 'WATCH', label: 'WATCHLIST', cmd: 'WL' },
      ].map((item) => (
        <button
          key={item.id}
          onClick={() => onNav(item.id)}
          className="w-full text-left px-3 py-1.5 text-[10px] font-bold text-fg hover:bg-acc/10 hover:text-acc transition-colors flex justify-between"
        >
          <span>{item.label}</span>
          <span className="text-[9px] opacity-30">{item.cmd}</span>
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-border-custom">
      <div className="text-[9px] text-acc2 font-bold animate-pulse">● LIVE CONNECTED</div>
      <div className="text-[8px] text-[#666] mt-1">GKE-FREE-01 // SG-1</div>
    </div>
  </aside>
);

const SignalFeed = () => {
  const [signals, setSignals] = useState<Signal[]>([]);

  // Mock signals for now
  useEffect(() => {
    setSignals([
      { id: 1, ticker: 'BBCA', title: 'INSIDER CLUSTER', body: '3 directors accumulating near 9000 support.', severity: 'HIGH', timestamp: '14:20:11' },
      { id: 2, ticker: 'GOTO', title: 'VOL ANOMALY', body: '300% volume spike vs 20d ADV.', severity: 'MED', timestamp: '13:45:02' },
      { id: 3, ticker: 'TLKM', title: 'BROKER FLOW', body: 'Heavy accumulation by foreign brokers.', severity: 'LOW', timestamp: '12:10:55' },
    ]);
  }, []);

  return (
    <aside className="w-[300px] border-l border-border-custom bg-black flex flex-col">
      <div className="p-2 border-b border-border-custom bg-surface text-[10px] font-bold text-acc tracking-tight uppercase">
        Intelligence Feed
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {signals.map((s) => (
          <div key={s.id} className={`p-2 border-l-2 ${
            s.severity === 'HIGH' ? 'border-acc3 bg-acc3/5' : 
            s.severity === 'MED' ? 'border-acc bg-acc/5' : 'border-acc4 bg-acc4/5'
          }`}>
            <div className="flex justify-between items-start mb-1">
              <span className="text-[10px] font-black text-white">{s.ticker}</span>
              <span className="text-[8px] text-[#666]">{s.timestamp}</span>
            </div>
            <div className="text-[10px] font-bold text-acc leading-tight mb-1">{s.title}</div>
            <p className="text-[9px] text-[#999] leading-tight">{s.body}</p>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default function Home() {
  const [data, setData] = useState<InsiderTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      const response = await fetch(`${apiUrl}/insider/latest`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`API Error: ${response.status}`);
      const json = await response.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="h-screen flex flex-col bg-bg text-fg font-mono overflow-hidden">
      {/* Scanline & CRT Effect */}
      <div className="scanline"></div>
      <div className="crt-overlay"></div>

      {/* Top Header */}
      <header className="h-8 bg-black border-b border-border-custom flex items-center px-4 justify-between z-10">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="text-acc font-black text-xs">IDX:TERMINAL</span>
            <span className="text-[#666] text-[10px] tracking-widest">ASIMMETRIC INTEL</span>
          </div>
          <div className="flex gap-4">
            <div className="text-[10px] text-acc2"><span className="opacity-50">IHSG</span> 7,234.12 <span className="text-[8px]">+0.12%</span></div>
            <div className="text-[10px] text-acc3"><span className="opacity-50">USDIDR</span> 15,670 <span className="text-[8px]">-0.05%</span></div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-[9px] text-[#666]">SUN MAY 10 2026 // 15:42:01 WIB</div>
          <div className="w-2 h-2 rounded-full bg-acc2 shadow-[0_0_5px_rgba(0,230,118,0.5)]"></div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar onNav={() => {}} />
        
        <main className="flex-1 flex flex-col bg-black border-r border-border-custom relative">
          {/* Main Panel Toolbar */}
          <div className="h-6 bg-surface border-b border-border-custom flex items-center px-2 justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-bold text-acc">VIEW: INSIDER_FEED</span>
              <span className="text-[9px] text-[#444]">|</span>
              <span className="text-[9px] text-[#888]">FILTER: ALL_SECTORS</span>
            </div>
            <div className="flex gap-2">
               <button onClick={fetchData} className="text-[9px] text-acc hover:underline">REFRESH</button>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-0">
            {loading ? (
              <div className="h-full flex items-center justify-center text-acc text-[10px] animate-pulse">
                INITIALIZING DATA PIPELINE...
              </div>
            ) : error ? (
              <div className="p-4 text-acc3 text-xs font-bold">ERROR: {error}</div>
            ) : (
              <table className="w-full dense-table">
                <thead>
                  <tr>
                    <th className="text-left">DATE</th>
                    <th className="text-left">TICKER</th>
                    <th className="text-left">INSIDER</th>
                    <th className="text-left">ROLE</th>
                    <th className="text-left">TYPE</th>
                    <th className="text-right">SHARES</th>
                    <th className="text-right">PRICE</th>
                    <th className="text-right">VALUE (IDR)</th>
                    <th className="text-center">CONF</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((row) => (
                    <tr key={row.id} className="hover:bg-acc/5 cursor-pointer">
                      <td className="text-[#666]">{row.date}</td>
                      <td className="text-acc4 font-black">{row.ticker}</td>
                      <td className="text-white font-bold">{row.insider_name}</td>
                      <td className="text-[#888]">{row.role}</td>
                      <td>
                        <span className={row.transaction_type === 'BUY' ? 'text-acc2' : 'text-acc3'}>
                          {row.transaction_type}
                        </span>
                      </td>
                      <td className="text-right font-mono">
                        {new Intl.NumberFormat('id-ID').format(typeof row.shares === 'string' ? parseFloat(row.shares) : row.shares)}
                      </td>
                      <td className="text-right font-mono text-acc">
                        {new Intl.NumberFormat('id-ID').format(typeof row.price === 'string' ? parseFloat(row.price) : row.price)}
                      </td>
                      <td className="text-right font-mono text-white">
                        {new Intl.NumberFormat('id-ID').format(typeof row.value === 'string' ? parseFloat(row.value) : row.value)}
                      </td>
                      <td className="text-center">
                        <span className={`px-1 rounded ${row.score >= 5 ? 'bg-acc2 text-black' : 'text-[#666]'}`}>
                          {row.score}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>

        <SignalFeed />
      </div>

      {/* Command Bar */}
      <footer className="h-6 bg-acc border-t border-border-custom flex items-center px-1 gap-2 z-10">
        <span className="text-black font-black text-[10px] px-1 bg-white">COMMAND</span>
        <input 
          type="text" 
          placeholder="ENTER COMMAND (e.g. INSIDER BBCA, FLOW GOTO)..."
          className="bg-transparent border-none outline-none text-black text-[10px] font-bold w-full placeholder:text-black/50"
          autoFocus
        />
        <div className="flex gap-4 px-2 whitespace-nowrap">
          <div className="text-[9px] font-black text-black">ALT+S: SEARCH</div>
          <div className="text-[9px] font-black text-black">ALT+Q: EXIT</div>
        </div>
      </footer>
    </div>
  );
}
