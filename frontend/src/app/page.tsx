'use client';

import React, { useEffect, useState, useCallback, useRef } from 'react';
import CommandPalette from './CommandPalette';
import { FlowView, AnomalyView, HeatmapView, WatchlistView } from './Views';

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
  ticker: string;
  insider_count: number;
  transaction_count: number;
  last_date: string;
  total_value: number;
  insiders: string[];
}

interface PriceLevel {
  price: number;
  shares: number;
  type: string;
}

interface AbsorptionData {
  ticker: string;
  total_shares_bought: number;
  adv_30d: number;
  absorption_ratio: number;
  current_price: number;
  transaction_count: number;
}

// --- Components ---

const Sidebar = ({ onNav, activeView, isScraping }: { onNav: (view: string) => void, activeView: string, isScraping: boolean }) => (
  <aside className="w-[200px] border-r border-border-custom bg-black flex flex-col z-20">
    <div className="p-4 border-b border-border-custom flex items-center gap-2">
      <div className="w-5 h-5 bg-acc rounded-sm"></div>
      <span className="font-bold text-[10px] tracking-tighter">IDX INSIDER</span>
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
          className={`w-full text-left px-3 py-1.5 text-[10px] font-bold transition-colors flex justify-between ${
            activeView === item.id ? 'bg-acc text-black' : 'text-fg hover:bg-acc/10 hover:text-acc'
          }`}
        >
          <span>{item.label}</span>
          <span className={`text-[9px] ${activeView === item.id ? 'text-black/50' : 'opacity-30'}`}>{item.cmd}</span>
        </button>
      ))}
    </nav>
    <div className="p-4 border-t border-border-custom">
      {isScraping && (
        <div className="text-[9px] text-acc font-bold animate-pulse mb-2 uppercase">
          [!] SCRAPING_ENGINE_ACTIVE
        </div>
      )}
      <div className="text-[9px] text-acc2 font-bold">● LIVE CONNECTED</div>
      <div className="text-[8px] text-[#666] mt-1">GKE-FREE-01 // SG-1</div>
    </div>
  </aside>
);

const SignalFeed = ({ isScraping }: { isScraping: boolean }) => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSignals = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/clusters`);
        if (res.ok) {
          const data = await res.json();
          setSignals(data);
        }
      } catch (e) {
        console.error("Signal fetch failed", e);
      } finally {
        setLoading(false);
      }
    };
    fetchSignals();
    const interval = setInterval(fetchSignals, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <aside className="w-[300px] border-l border-border-custom bg-black flex flex-col z-20">
      <div className="p-2 border-b border-border-custom bg-surface text-[10px] font-bold text-acc tracking-tight uppercase">
        Intelligence Feed
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-3">
        {loading ? (
          <div className="text-[10px] text-acc/50 animate-pulse p-2">SCANNING FOR CLUSTERS...</div>
        ) : signals.length === 0 ? (
          <div className="text-[10px] text-[#444] p-2 text-center mt-10 italic">
            {isScraping ? "SCRAPING IN PROGRESS..." : "NO ACTIVE CLUSTERS DETECTED"}
          </div>
        ) : signals.map((s, i) => (
          <div key={i} className="p-2 border-l-2 border-acc bg-acc/5">
            <div className="flex justify-between items-start mb-1">
              <span className="text-[10px] font-black text-white">{s.ticker}</span>
              <span className="text-[8px] text-[#666]">{s.last_date}</span>
            </div>
            <div className="text-[10px] font-bold text-acc leading-tight mb-1">INSIDER CLUSTER</div>
            <p className="text-[9px] text-[#999] leading-tight">
              {s.insider_count} unique insiders accumulating. Total Vol: {new Intl.NumberFormat('id-ID').format(s.total_value)} IDR.
            </p>
          </div>
        ))}
      </div>
    </aside>
  );
};

const InstitutionalDrawer = ({ ticker, transactionId, onClose }: { ticker: string, transactionId?: number, onClose: () => void }) => {
  const [priceMap, setPriceMap] = useState<PriceLevel[]>([]);
  const [absorption, setAbsorption] = useState<AbsorptionData | null>(null);
  const [narrative, setNarrative] = useState<{state: string, text: string} | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const [pmRes, absRes] = await Promise.all([
          fetch(`${apiUrl}/insider/accumulation/${ticker}`),
          fetch(`${apiUrl}/insider/absorption/${ticker}`)
        ]);
        if (pmRes.ok) setPriceMap(await pmRes.json());
        if (absRes.ok) setAbsorption(await absRes.json());
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [ticker]);

  const fetchNarrative = useCallback(async () => {
    if (!transactionId) return;
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/insider/narrative/${transactionId}`);
      
      if (res.ok) {
        const data = await res.json();
        setNarrative(data);
        if (data.state === 'QUEUED' || data.state === 'PROCESSING') {
          setTimeout(fetchNarrative, 3000);
        }
      } else if (res.status === 429) {
        setNarrative({ state: 'RATE_LIMITED', text: 'AI Capacity reached.' });
      } else {
        setNarrative({ state: 'DEGRADED', text: 'AI Narrative service temporarily degraded.' });
      }
    } catch (e) {
      setNarrative({ state: 'DEGRADED', text: 'Connection to AI service lost.' });
    }
  }, [transactionId]);

  useEffect(() => {
    fetchNarrative();
  }, [fetchNarrative]);

  const renderNarrative = () => {
    if (!narrative) return <div className="text-[10px] animate-pulse">INITIATING AI CHANNEL...</div>;

    switch (narrative.state) {
      case 'QUEUED':
      case 'PROCESSING':
        return (
          <div className="space-y-2">
            <div className="h-2 bg-acc/20 animate-pulse w-full"></div>
            <div className="h-2 bg-acc/20 animate-pulse w-3/4"></div>
            <div className="text-[8px] text-acc/60 font-bold animate-pulse uppercase">DECRYPTING LEDGER... [{narrative.state}]</div>
          </div>
        );
      case 'SUCCESS':
        return (
          <p className="text-[10px] leading-relaxed text-[#999] font-mono">
            {narrative.text}
          </p>
        );
      case 'FAILED_RETRYABLE':
      case 'TIMEOUT':
        return (
          <div className="space-y-2">
            <p className="text-[10px] text-acc3 italic">AI Analysis timed out or failed temporarily.</p>
            <button 
               onClick={() => fetchNarrative()}
               className="text-[9px] bg-acc3 text-black px-2 py-0.5 font-bold uppercase hover:bg-white transition-colors"
            >
              Retry Connection
            </button>
          </div>
        );
      case 'DEGRADED':
      case 'RATE_LIMITED':
        return (
          <div className="p-2 border border-acc3/30 bg-acc3/5">
             <p className="text-[10px] text-acc3 font-bold uppercase tracking-tighter">AI NARRATIVE TEMPORARILY UNAVAILABLE - PROVIDER LIMITS</p>
             <p className="text-[8px] text-acc3/60 mt-1 uppercase">NVIDIA NIM capacity exceeded or configuration missing.</p>
          </div>
        );
      case 'FAILED_FINAL':
        return <p className="text-[10px] text-acc3 font-bold uppercase">AI NARRATIVE GENERATION FAILED PERMANENTLY.</p>;
      case 'STALE':
        return <p className="text-[10px] text-[#666] font-bold uppercase italic">NARRATIVE STALE. RE-SCANNING...</p>;
      default:
        return <p className="text-[10px] text-[#999] font-mono">{narrative.text || 'NO DATA'}</p>;
    }
  };

  return (
    <div className="absolute inset-y-0 right-0 w-[400px] bg-black border-l border-acc shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-30 flex flex-col animate-in slide-in-from-right duration-300">
      <div className="p-2 bg-acc flex justify-between items-center">
        <span className="text-black font-black text-[10px] tracking-tighter">SECURITY_INTEL: {ticker}</span>
        <button onClick={onClose} className="text-black font-bold text-[10px] hover:bg-black/10 px-1">✕</button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {loading ? (
          <div className="h-full flex items-center justify-center text-acc text-[10px] animate-pulse">DECRYPTING ASYMMETRIC DATA...</div>
        ) : (
          <>
            {/* Absorption Section */}
            <section>
              <h3 className="text-[10px] font-black text-acc mb-2 uppercase tracking-widest border-b border-border-custom pb-1">Absorption Ratio</h3>
              {absorption && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="terminal-panel p-2">
                    <div className="text-[8px] text-[#666] uppercase">Ratio</div>
                    <div className={`text-4xl font-black ${absorption.absorption_ratio > 0.1 ? 'text-acc2' : 'text-acc'}`}>
                      {(absorption.absorption_ratio).toFixed(2)}x
                    </div>
                  </div>
                  <div className="terminal-panel p-2">
                    <div className="text-[8px] text-[#666] uppercase">30D ADV</div>
                    <div className="text-[10px] font-bold text-white">{new Intl.NumberFormat('id-ID').format(absorption.adv_30d)}</div>
                  </div>
                </div>
              )}
            </section>

            {/* Price Map Section */}
            <section>
              <h3 className="text-[10px] font-black text-acc mb-2 uppercase tracking-widest border-b border-border-custom pb-1">Accumulation Price Map</h3>
              <div className="space-y-1">
                {priceMap.map((level, i) => {
                  const maxShares = Math.max(...priceMap.map(l => l.shares));
                  const width = (level.shares / maxShares) * 100;
                  return (
                    <div key={i} className="flex items-center gap-2 text-[10px] font-mono">
                      <div className="w-12 text-[#666]">{level.price}</div>
                      <div className="flex-1 h-3 bg-surface relative">
                        <div 
                          className={`h-full ${level.type === 'BUY' ? 'bg-acc2/30' : 'bg-acc3/30'}`} 
                          style={{ width: `${width}%` }}
                        />
                        <div className="absolute inset-0 flex items-center px-1 text-[8px] font-bold">
                          {new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(level.shares)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* AI Summary Section */}
            <section className="terminal-panel p-3 bg-acc/5 border border-acc/20 relative overflow-hidden">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-[9px] font-black text-acc uppercase tracking-widest">NVIDIA_AI_NARRATIVE</h3>
                {narrative && (
                  <span className={`text-[7px] px-1 font-bold ${
                    narrative.state === 'SUCCESS' ? 'bg-acc2 text-black' : 
                    narrative.state === 'QUEUED' || narrative.state === 'PROCESSING' ? 'bg-acc text-black animate-pulse' :
                    'bg-acc3 text-black'
                  }`}>
                    {narrative.state}
                  </span>
                )}
              </div>
              
              {renderNarrative()}
            </section>
          </>
        )}
      </div>
    </div>
  );
};

const Clock = () => {
  const [time, setTime] = useState<string | null>(null);

  useEffect(() => {
    const update = () => {
      setTime(new Date().toLocaleString('en-US', { 
        weekday: 'short', month: 'short', day: '2-digit', year: 'numeric', 
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false 
      }));
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="text-[9px] text-[#666] uppercase min-w-[150px] text-right">
      {time ? `${time} WIB` : 'INITIALIZING...'}
    </div>
  );
};

const QuickStart = ({ onCommand, isScraping, ticker }: { onCommand: (cmd: string) => void, isScraping: boolean, ticker?: string | null }) => (
  <div className="flex flex-col items-center justify-center p-12 border-2 border-dashed border-acc/20 rounded-lg m-8 bg-acc/5">
    <div className="text-acc font-black text-xl mb-2 tracking-tighter">
      {ticker ? "SEARCHING EXCHANGE LEDGER..." : isScraping ? "SCRAPING_IN_PROGRESS" : "QUICK START TERMINAL"}
    </div>
    <p className="text-[#888] text-[10px] mb-8 max-w-md text-center uppercase">
      {ticker ? `Connecting to IDX nodes to retrieve asymmetric data for ${ticker}. Analyzing historical filings and real-time ledger entries.` : 
       isScraping ? "THE ENGINE IS CURRENTLY DECRYPTING NEW FILINGS FROM THE IDX EXCHANGE. DATA DENSITY WILL INCREASE SHORTLY." : 
      "Terminal initialized. No data matching current filters. Use the command bar or select a preset below to begin analysis."}
    </p>
    {(!isScraping && !ticker) && (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl">
        {[
          { label: 'INSIDER BBCA', desc: 'Deep dive into Bank Central Asia', cmd: 'INSIDER BBCA' },
          { label: 'FLOW GOTO', desc: 'Analyze GoTo Gojek Tokopedia flow', cmd: 'FLOW GOTO' },
          { label: 'HELP', desc: 'List all available terminal commands', cmd: 'HELP' },
        ].map((item) => (
          <button
            key={item.label}
            onClick={() => onCommand(item.cmd)}
            className="p-4 border border-acc/30 bg-black hover:bg-acc hover:text-black transition-all group text-left"
          >
            <div className="text-[10px] font-black mb-1">{item.label}</div>
            <div className="text-[9px] opacity-60 group-hover:opacity-100">{item.desc}</div>
          </button>
        ))}
      </div>
    )}
    {(isScraping || ticker) && (
      <div className="text-acc animate-pulse font-mono text-[10px] tracking-widest border border-acc px-4 py-2">
        {ticker ? `NODE_SCAN: ${ticker}_LEDGER_QUERY` : "CONNECTING TO EXCHANGE LEDGER..."}
      </div>
    )}
  </div>
);

export default function Home() {
  const [data, setData] = useState<InsiderTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCmdOpen, setIsCmdOpen] = useState(false);
  const [activeView, setActiveView] = useState('INSIDER');
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedTransactionId, setSelectedTransactionId] = useState<number | null>(null);
  const [commandValue, setCommandValue] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [marketData, setMarketData] = useState({ ihsg: 7234.12, ihsgChg: 0.12, usdidr: 15670, usdidrChg: -0.05 });

  const footerInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const checkScraper = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/scraper-status`);
        if (res.ok) {
          const status = await res.json();
          setIsScraping(status.is_running);
        }
      } catch (e) {
        console.error("Scraper status check failed", e);
      }
    };
    checkScraper();
    const interval = setInterval(checkScraper, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = useCallback(async (ticker?: string) => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = new URL(`${apiUrl}/insider/latest`);
      if (ticker) url.searchParams.append('ticker', ticker.toUpperCase());
      
      const res = await fetch(url.toString(), { cache: 'no-store' });
      if (!res.ok) throw new Error(`API Error: ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection error');
    } finally {
      setLoading(false);
    }
  }, []);

  const runTerminalCommand = useCallback((cmd: string) => {
    const val = cmd.trim().toUpperCase();
    if (!val) return;

    if (val === 'HELP') {
      alert("Available Commands:\nINSIDER [TICKER] - Show insider feed for ticker\nFLOW [TICKER] - Show smart flow for ticker\nHEATMAP - Show market heatmap\nANOMALY - Show market anomalies\nWL - Show watchlist\nALT+Q - Reset terminal\nESC - Close active drawer");
      return;
    }

    if (val.startsWith('INSIDER ')) {
      const parts = val.split(' ');
      if (parts.length > 1 && parts[1]) {
        const t = parts[1];
        setSelectedTicker(t);
        fetchData(t);
        setActiveView('INSIDER');
      }
    } else if (val.startsWith('FLOW ')) {
      const parts = val.split(' ');
      if (parts.length > 1 && parts[1]) {
        const t = parts[1];
        setSelectedTicker(t);
        setActiveView('FLOW');
      }
    } else if (val === 'HEATMAP' || val === 'MAP') {
      setActiveView('HEATMAP');
    } else if (val === 'ANOMALY') {
      setActiveView('ANOMALY');
    } else if (val === 'WL' || val === 'WATCH') {
      setActiveView('WATCH');
    } else {
      // Default to ticker search
      setSelectedTicker(val);
      fetchData(val);
    }
  }, [fetchData]);

  const handleCommand = (type: string, args: string[]) => {
    if (args.length > 0) {
      runTerminalCommand(`${type} ${args.join(' ')}`);
    } else {
      runTerminalCommand(type);
    }
  };

  const handleFooterCommand = (e: React.FormEvent) => {
    e.preventDefault();
    runTerminalCommand(commandValue);
    setCommandValue('');
  };

  useEffect(() => {
    fetchData();

    // Market data randomizer (Bloomberg feel)
    const marketInterval = setInterval(() => {
      setMarketData(prev => ({
        ...prev,
        ihsg: prev.ihsg + (Math.random() - 0.5) * 2,
        usdidr: prev.usdidr + (Math.random() - 0.5) * 5
      }));
    }, 5000);

    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedTicker(null);
        setIsCmdOpen(false);
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCmdOpen(prev => !prev);
      }
      if (e.altKey && e.key === 's') {
        e.preventDefault();
        footerInputRef.current?.focus();
      }
      if (e.altKey && e.key === 'q') {
        e.preventDefault();
        setSelectedTicker(null);
        setActiveView('INSIDER');
        fetchData();
      }
    };
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => {
      window.removeEventListener('keydown', handleGlobalKeyDown);
      clearInterval(marketInterval);
    };
  }, [fetchData, runTerminalCommand]);

  return (
    <div className="h-screen flex flex-col bg-bg text-fg font-mono overflow-hidden select-none">
      <div className="scanline"></div>
      <div className="crt-overlay"></div>

      {isCmdOpen && (
        <CommandPalette 
          onCommand={handleCommand} 
          onClose={() => setIsCmdOpen(false)} 
        />
      )}

      <header className="h-8 bg-black border-b border-border-custom flex items-center px-4 justify-between z-10">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-acc"></div>
            <span className="text-acc font-black text-xs">IDX:TERMINAL</span>
            <span className="text-[#666] text-[10px] tracking-widest">ASIMMETRIC INTEL</span>
          </div>
          <div className="flex gap-4">
            <div className="text-[10px] text-acc2">
              <span className="opacity-50">IHSG</span> {marketData.ihsg.toLocaleString('id-ID')} 
              <span className="text-[8px] ml-1">{marketData.ihsgChg > 0 ? '+' : ''}{marketData.ihsgChg}%</span>
            </div>
            <div className="text-[10px] text-acc3">
              <span className="opacity-50">USDIDR</span> {marketData.usdidr.toLocaleString('id-ID')} 
              <span className="text-[8px] ml-1">{marketData.usdidrChg > 0 ? '+' : ''}{marketData.usdidrChg}%</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Clock />
          <div className="w-2 h-2 rounded-full bg-acc2 shadow-[0_0_5px_rgba(0,230,118,0.5)]"></div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar onNav={setActiveView} activeView={activeView} isScraping={isScraping} />
        
        <main className="flex-1 flex flex-col bg-black border-r border-border-custom relative">
          <div className="h-6 bg-surface border-b border-border-custom flex items-center px-2 justify-between z-10">
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-bold text-acc">VIEW: {activeView}</span>
              <span className="text-[9px] text-[#444]">|</span>
              <span className="text-[9px] text-[#888]">FILTER: ALL_SECTORS</span>
            </div>
            <div className="flex gap-2">
               <button onClick={() => fetchData()} className="text-[9px] text-acc hover:underline uppercase font-bold">Refresh (F5)</button>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-0 relative">
            {loading && activeView === 'INSIDER' ? (
              <div className="h-full flex items-center justify-center text-acc text-[10px] animate-pulse">
                INITIALIZING DATA PIPELINE...
              </div>
            ) : error ? (
              <div className="p-4 text-acc3 text-xs font-bold">ERROR: {error}</div>
            ) : activeView === 'INSIDER' ? (
              data.length === 0 ? (
                <QuickStart onCommand={runTerminalCommand} isScraping={isScraping} ticker={selectedTicker} />
              ) : (
                <table className="w-full dense-table relative">
                  <thead className="sticky top-0 z-10">
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
                      <tr 
                        key={row.id} 
                        onClick={() => { setSelectedTicker(row.ticker); setSelectedTransactionId(row.id); }}
                        className={`hover:bg-acc/10 cursor-pointer ${selectedTicker === row.ticker ? 'bg-acc/20 border-l-2 border-acc' : ''}`}
                      >
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
                          <span className={`px-1 rounded text-[10px] font-bold ${row.score >= 7 ? 'bg-acc2 text-black' : row.score >= 4 ? 'bg-acc text-black' : 'text-[#666]'}`}>
                            {row.score}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            ) : activeView === 'FLOW' ? (
              <FlowView ticker={selectedTicker} />
            ) : activeView === 'ANOMALY' ? (
              <AnomalyView />
            ) : activeView === 'HEATMAP' ? (
              <HeatmapView />
            ) : activeView === 'WATCH' ? (
              <WatchlistView />
            ) : (
              <div className="p-4 text-acc text-[10px]">UNKNOWN VIEW STATE</div>
            )}

            {selectedTicker && activeView === 'INSIDER' && (
              <InstitutionalDrawer 
                ticker={selectedTicker} 
                transactionId={selectedTransactionId || undefined} 
                onClose={() => { setSelectedTicker(null); setSelectedTransactionId(null); }} 
              />
            )}
          </div>
        </main>

        <SignalFeed isScraping={isScraping} />
      </div>

      <footer className="h-6 bg-acc border-t border-border-custom flex items-center px-1 gap-2 z-40 relative">
        <span className="text-black font-black text-[10px] px-1 bg-white">COMMAND</span>
        <form onSubmit={handleFooterCommand} className="flex-1">
          <input 
            ref={footerInputRef}
            type="text" 
            value={commandValue}
            onChange={(e) => setCommandValue(e.target.value)}
            placeholder="ENTER COMMAND (e.g. INSIDER BBCA, FLOW GOTO)..."
            className="bg-transparent border-none outline-none text-black text-[10px] font-bold w-full placeholder:text-black/50"
          />
        </form>
        <div className="flex gap-4 px-2 whitespace-nowrap">
          <div className="text-[9px] font-black text-black uppercase tracking-tighter">ALT+S: SEARCH</div>
          <div className="text-[9px] font-black text-black uppercase tracking-tighter">ALT+Q: RESET</div>
        </div>
      </footer>
    </div>
  );
}
