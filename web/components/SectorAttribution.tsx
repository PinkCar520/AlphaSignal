import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { ChevronRight, ChevronDown } from 'lucide-react';

interface SubSectorStat {
  impact: number;
  weight: number;
}

interface SectorStat {
  impact: number;
  weight: number;
  sub: Record<string, SubSectorStat>;
}

interface Props {
  data: Record<string, SectorStat>;
}

export function SectorAttribution({ data }: Props) {
  const t = useTranslations('Funds');
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  
  if (!data || Object.keys(data).length === 0) return null;

  const toggleExpand = (name: string) => {
    setExpanded(prev => ({ ...prev, [name]: !prev[name] }));
  };

  const sectors = Object.entries(data)
    .map(([name, stat]) => ({ name, ...stat }))
    .sort((a, b) => b.impact - a.impact);

  // Global Max for bar scaling
  const maxImpact = Math.max(...sectors.map(s => Math.abs(s.impact)), 0.01);

  return (
    <div className="mt-4 border-t border-slate-100 pt-4">
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
           {t('sectorAttribution')}
        </h3>
        <span className="text-[10px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-100">
           {t('byShenwanL1')}
        </span>
      </div>
      
      <div className="space-y-1">
        {sectors.map((sector) => {
            const isExpanded = expanded[sector.name];
            const subSectors = Object.entries(sector.sub || {})
                .map(([n, s]) => ({ name: n, ...s }))
                .sort((a, b) => b.impact - a.impact);
            const hasSub = subSectors.length > 0;

            return (
              <div key={sector.name} className="flex flex-col">
                {/* L1 Row */}
                <div 
                  onClick={() => hasSub && toggleExpand(sector.name)}
                  className={`group flex items-center text-xs py-1.5 px-2 rounded cursor-pointer transition-colors ${isExpanded ? 'bg-slate-50' : 'hover:bg-slate-50'}`}
                >
                  {/* Name & Toggle */}
                  <div className="w-32 shrink-0 flex items-center gap-1">
                    <div className={`text-slate-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`}>
                        {hasSub ? <ChevronRight className="w-3 h-3" /> : <div className="w-3 h-3"/>}
                    </div>
                    <div>
                        <div className="font-bold text-slate-700">{sector.name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">{sector.weight.toFixed(2)}%</div>
                    </div>
                  </div>
                  
                  {/* Bar Chart Area */}
                  <div className="flex-1 px-4 flex items-center justify-center relative h-5">
                     <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-200"></div>
                     <div className="w-full flex">
                       <div className="flex-1 flex justify-end">
                          {sector.impact < 0 && (
                              <div 
                                className="h-2.5 bg-emerald-500 rounded-l-sm"
                                style={{ width: `${(Math.abs(sector.impact) / maxImpact) * 100}%` }}
                              ></div>
                          )}
                       </div>
                       <div className="flex-1 flex justify-start">
                          {sector.impact > 0 && (
                              <div 
                                className="h-2.5 bg-rose-500 rounded-r-sm"
                                style={{ width: `${(sector.impact / maxImpact) * 100}%` }}
                              ></div>
                          )}
                       </div>
                     </div>
                  </div>
                  
                  {/* Value */}
                  <div className={`w-16 shrink-0 text-right font-mono font-bold ${sector.impact >= 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {sector.impact > 0 ? '+' : ''}{sector.impact.toFixed(2)}%
                  </div>
                </div>

                {/* L2 Rows (Drill-down) */}
                {isExpanded && hasSub && (
                    <div className="ml-4 pl-4 border-l-2 border-slate-100 py-1 space-y-1 bg-slate-50/50 rounded-r-lg mb-2">
                        {subSectors.map(sub => (
                            <div key={sub.name} className="flex items-center text-[11px] py-1 px-2">
                                <div className="w-28 shrink-0">
                                    <div className="text-slate-600 font-medium">{sub.name}</div>
                                    <div className="text-[9px] text-slate-400 font-mono">{sub.weight.toFixed(2)}%</div>
                                </div>
                                <div className="flex-1 px-4 flex items-center justify-center relative h-3">
                                     <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-200/50"></div>
                                     <div className="w-full flex opacity-80">
                                       <div className="flex-1 flex justify-end">
                                          {sub.impact < 0 && (
                                              <div 
                                                className="h-1.5 bg-emerald-400 rounded-l-sm"
                                                style={{ width: `${(Math.abs(sub.impact) / maxImpact) * 100}%` }}
                                              ></div>
                                          )}
                                       </div>
                                       <div className="flex-1 flex justify-start">
                                          {sub.impact > 0 && (
                                              <div 
                                                className="h-1.5 bg-rose-400 rounded-r-sm"
                                                style={{ width: `${(sub.impact / maxImpact) * 100}%` }}
                                              ></div>
                                          )}
                                       </div>
                                     </div>
                                </div>
                                <div className={`w-16 shrink-0 text-right font-mono ${sub.impact >= 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                    {sub.impact > 0 ? '+' : ''}{sub.impact.toFixed(2)}%
                                </div>
                            </div>
                        ))}
                    </div>
                )}
              </div>
            );
        })}
      </div>
    </div>
  );
}