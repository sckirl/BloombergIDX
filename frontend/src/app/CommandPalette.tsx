'use client';

import React, { useState, useEffect, useRef } from 'react';

interface CommandPaletteProps {
  onCommand: (cmd: string, args: string[]) => void;
  onClose: () => void;
}

export default function CommandPalette({ onCommand, onClose }: CommandPaletteProps) {
  const [input, setInput] = useState('');
  const [results, setResults] = useState<{ label: string; cmd: string }[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
    if (e.key === 'Enter') {
      executeCommand(input);
    }
  };

  const executeCommand = (val: string) => {
    const raw = val.trim().toUpperCase();
    
    // Rigid Regex Routing (CMD-PAL-01)
    const routes = [
      { regex: /^INSIDER\s+([A-Z]{4})$/, type: 'INSIDER' },
      { regex: /^FLOW\s+([A-Z]{4})$/, type: 'FLOW' },
      { regex: /^MAP$/, type: 'HEATMAP' },
      { regex: /^WL$/, type: 'WATCHLIST' },
      { regex: /^HELP$/, type: 'HELP' },
    ];

    for (const route of routes) {
      const match = raw.match(route.regex);
      if (match) {
        onCommand(route.type, match.slice(1));
        onClose();
        return;
      }
    }

    // Default search fallback
    onCommand('SEARCH', [raw]);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative w-full max-w-xl bg-surface border border-acc shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
        <div className="flex items-center gap-2 p-3 border-b border-border-custom bg-black">
          <span className="text-acc font-black text-xs">CMD {'>'}</span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="ENTER TERMINAL COMMAND (e.g. INSIDER BBCA)..."
            className="flex-1 bg-transparent border-none outline-none text-fg text-xs font-mono placeholder:text-[#444]"
          />
        </div>
        
        <div className="p-2 bg-black/50">
          <div className="text-[9px] text-[#666] font-bold uppercase tracking-widest mb-2 px-2">Suggestions</div>
          {[
            { label: 'Check BBCA Insiders', cmd: 'INSIDER BBCA' },
            { label: 'View Smart Money Flow', cmd: 'FLOW GOTO' },
            { label: 'Open Sector Heatmap', cmd: 'MAP' },
            { label: 'System Help', cmd: 'HELP' },
          ].map((item, i) => (
            <button
              key={i}
              onClick={() => executeCommand(item.cmd)}
              className="w-full text-left px-2 py-1.5 text-[10px] text-[#999] hover:text-acc hover:bg-acc/5 transition-colors flex justify-between"
            >
              <span>{item.label}</span>
              <span className="font-bold opacity-50">{item.cmd}</span>
            </button>
          ))}
        </div>
        
        <div className="bg-acc px-2 py-1 flex justify-between items-center">
          <span className="text-black font-black text-[9px]">BLOOMBERG-IDX v1.0</span>
          <span className="text-black font-bold text-[9px]">ESC TO CANCEL</span>
        </div>
      </div>
    </div>
  );
}
