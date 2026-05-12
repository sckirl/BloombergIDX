'use client';

import React, { useEffect, useState } from 'react';

// --- Flow View ---
export const FlowView = ({ ticker }: { ticker: string | null }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!ticker) return;
    const fetchFlow = async () => {
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/flow/${ticker}`);
        if (res.ok) {
          setData(await res.json());
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchFlow();
  }, [ticker]);

  if (!ticker) return (
    <div className="h-full flex flex-col items-center justify-center p-10 text-center">
      <div className="text-acc font-black text-xl mb-4">SMART MONEY FLOW</div>
      <p className="text-[#666] text-xs max-w-md">Enter a ticker in the command bar (e.g., <span className="text-acc">FLOW BBCA</span>) to analyze institutional broker accumulation and distribution patterns.</p>
    </div>
  );

  if (loading) return <div className="p-10 text-acc animate-pulse text-[10px]">SCANNING BROKER LEDGERS...</div>;

  return (
    <div className="p-2 space-y-4 font-mono">
      <div className="flex justify-between items-end border-b border-acc pb-1">
        <div>
          <h2 className="text-sm font-black text-white">{ticker}</h2>
          <p className="text-[10px] text-acc uppercase tracking-tighter">Institutional Broker Flow (30D)</p>
        </div>
        <div className="text-right">
          <div className="text-[9px] text-[#666] uppercase">Concentration</div>
          <div className={`text-xl font-black ${data?.concentration > 0.5 ? 'text-acc2' : 'text-acc'}`}>
            {data ? (data.concentration * 100).toFixed(0) : '0'}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        <div className="terminal-panel p-2 bg-acc/5">
          <h3 className="text-[10px] font-bold text-acc mb-2 uppercase border-b border-acc/20 pb-1">Top Accumulating Brokers</h3>
          <table className="w-full text-[10px] tracking-tighter">
            <thead>
              <tr className="text-[#666] border-b border-border-custom text-left">
                <th className="pb-1 font-bold">BROKER</th>
                <th className="text-right pb-1 font-bold">NET VALUE (IDR)</th>
              </tr>
            </thead>
            <tbody>
              {data?.top_buyers?.map((row: any, i: number) => (
                <tr key={i} className="border-b border-border-custom/50">
                  <td className="py-1 text-white font-bold">{row.broker_code} <span className="text-[8px] font-normal text-[#666]">{row.broker_name?.substring(0, 12)}</span></td>
                  <td className="py-1 text-right text-acc2 font-bold">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(row.net_value)}</td>
                </tr>
              )) || <tr><td colSpan={2} className="py-4 text-center text-[#444]">NO DATA</td></tr>}
            </tbody>
          </table>
        </div>

        <div className="terminal-panel p-2 bg-acc/5">
          <h3 className="text-[10px] font-bold text-acc mb-2 uppercase border-b border-acc/20 pb-1">Top Distributing Brokers</h3>
          <table className="w-full text-[10px] tracking-tighter">
            <thead>
              <tr className="text-[#666] border-b border-border-custom text-left">
                <th className="pb-1 font-bold">BROKER</th>
                <th className="text-right pb-1 font-bold">NET VALUE (IDR)</th>
              </tr>
            </thead>
            <tbody>
              {data?.top_sellers?.map((row: any, i: number) => (
                <tr key={i} className="border-b border-border-custom/50">
                  <td className="py-1 text-white font-bold">{row.broker_code} <span className="text-[8px] font-normal text-[#666]">{row.broker_name?.substring(0, 12)}</span></td>
                  <td className="py-1 text-right text-acc3 font-bold">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(Math.abs(row.net_value))}</td>
                </tr>
              )) || <tr><td colSpan={2} className="py-4 text-center text-[#444]">NO DATA</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      <div className="terminal-panel p-2 bg-black border border-acc/20">
         <div className="grid grid-cols-3 gap-2">
            <div>
              <div className="text-[8px] text-[#666] uppercase">Buy Vol</div>
              <div className="text-[10px] font-bold text-acc2">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(data?.summary?.total_buy_value || 0)}</div>
            </div>
            <div>
              <div className="text-[8px] text-[#666] uppercase">Sell Vol</div>
              <div className="text-[10px] font-bold text-acc3">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(data?.summary?.total_sell_value || 0)}</div>
            </div>
            <div>
              <div className="text-[8px] text-[#666] uppercase">Nodes</div>
              <div className="text-[10px] font-bold text-white">{data?.summary?.total_brokers || 0}</div>
            </div>
         </div>
      </div>
    </div>
  );
};

// --- Anomaly View ---
export const AnomalyView = () => {
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/anomalies`);
        if (res.ok) {
          setAnomalies(await res.json());
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAnomalies();
  }, []);

  return (
    <div className="p-2 space-y-2 font-mono">
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-3 h-3 ${loading ? 'bg-acc animate-pulse' : 'bg-acc3'}`}></div>
        <h2 className="text-[10px] font-black text-white tracking-widest uppercase">Market Volumetric Anomalies</h2>
      </div>

      {loading ? (
        <div className="text-acc text-[10px] animate-pulse">DETECTING VOLUMETRIC SIGMAS...</div>
      ) : anomalies.length === 0 ? (
        <div className="text-[#444] text-[10px] italic p-10 text-center border border-dashed border-[#222]">NO SIGNIFICANT ANOMALIES DETECTED</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
          {anomalies.map((item, i) => (
            <div key={i} className="terminal-panel p-2 border-l-2 border-acc3 bg-acc3/5">
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm font-black text-white">{item.ticker}</span>
                <span className={`text-[7px] px-1 font-bold ${item.anomaly_score > 50 ? 'bg-acc3 text-black' : 'text-acc3 border border-acc3'}`}>
                  {item.anomaly_score > 50 ? 'CRIT' : item.anomaly_score > 20 ? 'HIGH' : 'MED'}
                </span>
              </div>
              <div className="text-[9px] font-bold text-acc3 mb-1 truncate">
                {item.rvol > 3 ? 'VOLUME_SPIKE' : 'PRICE_ANOMALY'}
              </div>
              <div className="text-[9px] text-[#777] leading-tight mb-2 border-t border-white/5 pt-1">
                RV: <span className="text-white">{item.rvol.toFixed(1)}x</span> | CHG: <span className={item.price_change > 0 ? 'text-acc2' : 'text-acc3'}>{(item.price_change * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center text-[7px]">
                <span className="text-[#555]">SIGMA_SCORE</span>
                <span className="text-acc3 font-bold">{item.anomaly_score.toFixed(1)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// --- Heatmap View ---
export const HeatmapView = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHeatmap = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/heatmap`);
        if (res.ok) {
          setData(await res.json());
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchHeatmap();
  }, []);

  return (
    <div className="p-2 h-full flex flex-col font-mono">
      <h2 className="text-[10px] font-bold text-acc mb-2 uppercase tracking-widest border-b border-acc/20 pb-1">Sector Accumulation Heatmap (30D)</h2>
      
      {loading ? (
        <div className="flex-1 flex items-center justify-center text-acc text-[10px] animate-pulse">AGGREGATING SECTOR FLOWS...</div>
      ) : data.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-[#444] text-[10px] italic">NO SECTOR ACTIVITY DATA AVAILABLE</div>
      ) : (
        <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-1 overflow-auto">
          {data.map((s, i) => (
            <div key={i} className={`border border-border-custom p-2 flex flex-col ${s.net_flow > 0 ? 'bg-acc2/5' : 'bg-acc3/5'}`}>
              <div className="flex justify-between items-start mb-1">
                <div className="text-[9px] font-black text-white truncate w-24 uppercase">{s.sector}</div>
                <div className={`text-[8px] font-bold ${s.net_flow > 0 ? 'text-acc2' : 'text-acc3'}`}>
                  {new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(s.net_flow)}
                </div>
              </div>
              <div className="flex-1 flex flex-col justify-center items-center py-2 border border-white/5 bg-black/20">
                <div className="text-sm font-black text-white tracking-tighter">{s.top_ticker || 'N/A'}</div>
                <div className="text-[7px] text-[#666] uppercase">Top Mover</div>
              </div>
              <div className="mt-1 flex justify-between items-center">
                <span className="text-[7px] text-[#444]">{s.trade_count} TRADES</span>
                <span className={`text-[7px] font-bold ${s.sentiment === 'BULLISH' ? 'text-acc2' : 'text-acc3'}`}>{s.sentiment}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// --- Watchlist View ---
export const WatchlistView = () => {
  return (
    <div className="p-4">
      <h2 className="text-[10px] font-bold text-acc mb-6 uppercase tracking-widest">Institutional Watchlist</h2>
      <table className="w-full text-[10px]">
        <thead>
          <tr className="text-[#666] border-b border-border-custom">
            <th className="text-left pb-2">TICKER</th>
            <th className="text-right pb-2">PRICE</th>
            <th className="text-right pb-2">CHG%</th>
            <th className="text-right pb-2">INSIDER_BUY</th>
            <th className="text-right pb-2">SMART_FLOW</th>
            <th className="text-center pb-2">SIGNAL</th>
          </tr>
        </thead>
        <tbody>
          {[
            { t: 'BBCA', p: '9,850', c: '+0.51', i: 'HIGH', f: 'NEUTRAL', s: 'HOLD' },
            { t: 'GOTO', p: '64', c: '-3.03', i: 'LOW', f: 'BULLISH', s: 'ACCUM' },
            { t: 'ADRO', p: '2,840', c: '+4.20', i: 'HIGH', f: 'BULLISH', s: 'BUY' },
            { t: 'TLKM', p: '3,820', c: '-0.26', i: 'MED', f: 'BEARISH', s: 'WATCH' },
          ].map((row, i) => (
            <tr key={i} className="border-b border-border-custom hover:bg-white/5 cursor-pointer">
              <td className="py-3 font-black text-white">{row.t}</td>
              <td className="py-3 text-right font-mono">{row.p}</td>
              <td className={`py-3 text-right font-mono ${row.c.startsWith('+') ? 'text-acc2' : 'text-acc3'}`}>{row.c}%</td>
              <td className="py-3 text-right font-bold">{row.i}</td>
              <td className="py-3 text-right font-bold">{row.f}</td>
              <td className="py-3 text-center">
                <span className={`px-2 py-0.5 rounded-sm font-black ${row.s === 'BUY' ? 'bg-acc2 text-black' : row.s === 'ACCUM' ? 'text-acc2 border border-acc2' : 'text-[#666]'}`}>
                  {row.s}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-8 p-4 border border-dashed border-acc/30 text-center">
        <p className="text-[9px] text-[#555]">USE <span className="text-acc">WL ADD [TICKER]</span> TO TRACK NEW SECURITIES</p>
      </div>
    </div>
  );
};
