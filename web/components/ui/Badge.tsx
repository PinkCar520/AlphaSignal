import React from 'react';

interface BadgeProps {
  variant?: 'neutral' | 'bullish' | 'bearish' | 'gold' | 'outline';
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = 'neutral', children, className = '' }: BadgeProps) {
  const variants = {
    neutral: "bg-slate-800 text-slate-300 border-slate-700",
    bullish: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]",
    bearish: "bg-rose-500/10 text-rose-400 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]",
    gold: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20 shadow-[0_0_10px_rgba(234,179,8,0.1)]",
    outline: "bg-transparent",
  };

  const baseClasses = "px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider border";
  const combinedClasses = `${baseClasses} ${variants[variant]} ${className}`.trim();

  return (
    <span className={combinedClasses}>
      {children}
    </span>
  );
}
