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
              <div className="flex justify-between items-center text-[7px] mb-1">
                <span className="text-[#555]">VOL_MULT</span>
                <span className="text-white">{item.rvol.toFixed(2)}x</span>
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
export const HeatmapView = ({ onSelectTicker }: { onSelectTicker?: (t: string) => void }) => {
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
        <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-2 overflow-auto">
          {data.map((s, i) => {
            const maxFlow = Math.max(...data.map(d => Math.abs(d.net_flow)));
            const barWidth = (Math.abs(s.net_flow) / maxFlow) * 100;
            return (
              <div key={i} className={`border border-border-custom p-3 flex flex-col relative overflow-hidden ${s.net_flow > 0 ? 'bg-acc2/5' : 'bg-acc3/5'}`}>
                {/* Visual Flow Bar */}
                <div 
                  className={`absolute bottom-0 left-0 h-1 transition-all duration-1000 ${s.net_flow > 0 ? 'bg-acc2 shadow-[0_0_5px_rgba(0,230,118,0.5)]' : 'bg-acc3 shadow-[0_0_5px_rgba(255,23,68,0.5)]'}`}
                  style={{ width: `${barWidth}%` }}
                />
                
                <div className="flex justify-between items-start mb-2 relative z-10">
                  <div className="text-[10px] font-black text-white truncate w-32 uppercase tracking-tighter">{s.sector}</div>
                  <div className={`text-[9px] font-black px-1 ${s.net_flow > 0 ? 'bg-acc2 text-black' : 'bg-acc3 text-white'}`}>
                    {s.net_flow > 0 ? '+' : ''}{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(s.net_flow)}
                  </div>
                </div>

                <div className="flex-1 flex flex-col justify-center items-center py-4 border border-white/5 bg-black/40 group cursor-pointer hover:border-acc/50 transition-colors relative z-10"
                     onClick={() => s.top_ticker && onSelectTicker?.(s.top_ticker)}
                >
                  <div className="text-[8px] text-[#555] uppercase font-bold mb-1">Top Sector Mover</div>
                  <div className="text-lg font-black text-white tracking-tighter group-hover:text-acc underline decoration-acc/30">{s.top_ticker || 'N/A'}</div>
                </div>

                <div className="mt-3 space-y-1.5 relative z-10 border-t border-white/5 pt-2">
                  <div className="flex justify-between items-center text-[8px]">
                     <span className="text-[#666] uppercase">52W Range</span>
                     <span className="text-fg font-bold">
                       {new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(s.avg_52w_low)} 
                       <span className="mx-1 opacity-30">-</span> 
                       {new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(s.avg_52w_high)}
                     </span>
                  </div>
                  <div className="flex justify-between items-center text-[8px]">
                     <span className="text-[#666] uppercase">Avg Daily Vol</span>
                     <span className="text-[#888]">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(s.avg_volume)}</span>
                  </div>
                </div>
                
                <div className="mt-2 pt-1 flex justify-between items-center relative z-10">
                  <span className="text-[8px] text-[#444] font-bold tracking-widest">{s.trade_count} NODES</span>
                  <span className={`text-[8px] font-black tracking-widest ${s.sentiment === 'BULLISH' ? 'text-acc2' : 'text-acc3'}`}>{s.sentiment}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// --- Watchlist View ---
export const WatchlistView = ({ onSelectTicker }: { onSelectTicker?: (t: string) => void }) => {
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const wl = JSON.parse(localStorage.getItem('watchlist') || '["BBCA", "GOTO", "TLKM", "ASII"]');
    setWatchlist(wl);
  }, []);

  useEffect(() => {
    if (watchlist.length === 0) {
      setLoading(false);
      return;
    }

    const fetchWatchlistData = async () => {
      setLoading(true);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/watchlist-data?tickers=${watchlist.join(',')}`);
        if (res.ok) {
          setData(await res.json());
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchWatchlistData();
  }, [watchlist]);

  return (
    <div className="p-4 font-mono">
      <h2 className="text-[10px] font-bold text-acc mb-6 uppercase tracking-widest">Institutional Watchlist</h2>
      
      {loading ? (
        <div className="text-acc text-[10px] animate-pulse">CONNECTING TO NODES...</div>
      ) : watchlist.length === 0 ? (
        <div className="text-[#444] text-[10px] italic p-10 text-center border border-dashed border-[#222]">WATCHLIST EMPTY</div>
      ) : (
        <table className="w-full text-[10px]">
          <thead>
            <tr className="text-[#666] border-b border-border-custom">
              <th className="text-left pb-2">TICKER</th>
              <th className="text-right pb-2">PRICE</th>
              <th className="text-right pb-2">CHG%</th>
              <th className="text-right pb-2">52W RANGE</th>
              <th className="text-right pb-2">AVG VOL</th>
              <th className="text-right pb-2">INSIDER_BUY</th>
              <th className="text-center pb-2">SIGNAL</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="border-b border-border-custom hover:bg-white/5 cursor-pointer"
                  onClick={() => onSelectTicker?.(row.ticker)}
              >
                <td className="py-3 font-black text-white">{row.ticker}</td>
                <td className="py-3 text-right font-mono">{new Intl.NumberFormat('id-ID').format(row.price)}</td>
                <td className={`py-3 text-right font-mono ${row.change_pct > 0 ? 'text-acc2' : 'text-acc3'}`}>{row.change_pct > 0 ? '+' : ''}{row.change_pct}%</td>
                <td className="py-3 text-right text-[8px] text-[#666]">
                  {new Intl.NumberFormat('id-ID').format(row.fifty_two_week_low)} - {new Intl.NumberFormat('id-ID').format(row.fifty_two_week_high)}
                </td>
                <td className="py-3 text-right text-[#888]">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(row.avg_volume)}</td>
                <td className="py-3 text-right font-bold text-acc">{row.insider_buy_level}</td>
                <td className="py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-sm font-black ${row.signal === 'BUY' ? 'bg-acc2 text-black' : row.signal === 'ACCUM' ? 'text-acc2 border border-acc2' : 'text-[#666]'}`}>
                    {row.signal}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      
      <div className="mt-8 p-4 border border-dashed border-acc/30 text-center">
        <p className="text-[9px] text-[#555]">USE <span className="text-acc">WL ADD [TICKER]</span> TO TRACK NEW SECURITIES</p>
      </div>
    </div>
  );
};

// --- Event View ---
export const EventView = ({ onSelectTicker }: { onSelectTicker?: (t: string) => void }) => {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${apiUrl}/insider/events`);
        if (res.ok) {
          setEvents(await res.json());
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchEvents();
  }, []);

  return (
    <div className="p-4 font-mono space-y-6">
      <h2 className="text-[10px] font-bold text-acc mb-4 uppercase tracking-widest border-b border-acc/20 pb-1">Corporate Event Intelligence (E-IPO & Mergers)</h2>
      
      {loading ? (
        <div className="text-acc text-[10px] animate-pulse">DECRYPTING EVENT LEDGERS...</div>
      ) : events.length === 0 ? (
        <div className="text-[#444] text-[10px] italic p-10 text-center border border-dashed border-[#222]">NO ACTIVE EVENTS DETECTED</div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {events.map((event, i) => (
            <div key={i} className="terminal-panel p-3 border-l-2 border-acc bg-acc/5 flex flex-col md:flex-row gap-4">
              <div className="flex-1 space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[8px] bg-white text-black px-1 font-black mr-2">{event.event_type}</span>
                    <span className="text-xs font-black text-white">{event.company_name}</span>
                    {event.ticker && (
                      <span 
                        onClick={() => onSelectTicker?.(event.ticker)}
                        className="text-acc ml-2 cursor-pointer hover:underline"
                      >
                        [{event.ticker}]
                      </span>
                    )}
                  </div>
                  <span className="text-[8px] text-[#666]">{event.event_date}</span>
                </div>
                
                <p className="text-[10px] text-[#999] leading-tight italic">"{event.description}"</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
                  {event.event_type === 'E-IPO' ? (
                    <>
                      <div>
                        <div className="text-[7px] text-[#555] uppercase">Underwriter</div>
                        <div className="text-[9px] font-bold text-white">{event.underwriter}</div>
                      </div>
                      <div>
                        <div className="text-[7px] text-[#555] uppercase">Price Range</div>
                        <div className="text-[9px] font-bold text-acc2">{event.offering_price_range}</div>
                      </div>
                      <div>
                        <div className="text-[7px] text-[#555] uppercase">Total Shares</div>
                        <div className="text-[9px] font-bold text-white">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(event.total_shares)}</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <div className="text-[7px] text-[#555] uppercase">Acquirer</div>
                        <div className="text-[9px] font-bold text-white">{event.acquirer}</div>
                      </div>
                      <div>
                        <div className="text-[7px] text-[#555] uppercase">Target</div>
                        <div className="text-[9px] font-bold text-white">{event.target}</div>
                      </div>
                      <div>
                        <div className="text-[7px] text-[#555] uppercase">Fair Value (KJPP)</div>
                        <div className="text-[9px] font-bold text-acc2">{new Intl.NumberFormat('id-ID', { notation: 'compact' }).format(event.fair_value)}</div>
                      </div>
                    </>
                  )}
                  <div>
                    <div className="text-[7px] text-[#555] uppercase">Status</div>
                    <div className={`text-[9px] font-black ${event.status === 'COMPLETED' ? 'text-acc2' : 'text-acc'}`}>{event.status}</div>
                  </div>
                </div>
              </div>
              
              <div className="md:w-32 flex items-center justify-center border-l border-white/5 pl-4">
                 <a href={event.source_url} target="_blank" rel="noreferrer" className="text-[8px] border border-acc/30 px-2 py-1 hover:bg-acc hover:text-black transition-colors uppercase font-bold">View Prospectus</a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
