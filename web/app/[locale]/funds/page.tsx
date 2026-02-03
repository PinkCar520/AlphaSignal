'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Search, RefreshCw, ArrowUp, ArrowDown, PieChart, X } from 'lucide-react';

interface ComponentStock {
    code: string;
    name: string;
    price: number;
    change_pct: number;
    impact: number;
    weight: number;
}

interface FundValuation {
    fund_code: string;
    fund_name?: string;
    estimated_growth: number;
    total_weight: number;
    components: ComponentStock[];
    timestamp: string;
}

interface WatchlistItem {
    code: string;
    name: string;
}

export default function FundDashboard({ params }: { params: Promise<{ locale: string }> }) {
    const { locale } = React.use(params);
    const t = useTranslations('Funds');

    const [watchlist, setWatchlist] = useState<WatchlistItem[]>([
        { code: '022365', name: '永赢科技智选混合C' },
        { code: '020840', name: '南方中证半导体C' }
    ]);
    const [selectedFund, setSelectedFund] = useState<string>('022365');
    const [valuation, setValuation] = useState<FundValuation | null>(null);
    const [loading, setLoading] = useState(false);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

    const fetchValuation = async (code: string) => {
        setLoading(true);
        try {
            const res = await fetch(`/api/funds/${code}/valuation`);
            const data = await res.json();
            if (data.error) {
                console.error(data.error);
                return;
            }
            setValuation(data);
            setLastUpdated(new Date());

            // Auto-update name in watchlist if found
            if (data.fund_name) {
                setWatchlist(prev => prev.map(item =>
                    item.code === code && !item.name ? { ...item, name: data.fund_name } : item
                ));
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (selectedFund) {
            fetchValuation(selectedFund);
        }
    }, [selectedFund]);

    // Auto refresh every 60s
    useEffect(() => {
        const interval = setInterval(() => {
            if (selectedFund) fetchValuation(selectedFund);
        }, 60000);
        return () => clearInterval(interval);
    }, [selectedFund]);

    const handleDelete = (e: React.MouseEvent, codeToDelete: string) => {
        e.stopPropagation();
        setWatchlist(prev => prev.filter(item => item.code !== codeToDelete));
        if (selectedFund === codeToDelete) {
            // If deleting active, switch to first available or empty
            const remaining = watchlist.filter(i => i.code !== codeToDelete);
            if (remaining.length > 0) setSelectedFund(remaining[0].code);
            else setSelectedFund("");
        }
    };

    return (
        <div className="min-h-screen p-4 md:p-6 lg:p-8 font-sans bg-[#020617] text-slate-100">
            <header className="mb-8">
                <h1 className="text-3xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 flex items-center gap-3">
                    <span>🔮</span>
                    {t('title')}
                </h1>
                <p className="text-slate-500 font-mono text-xs mt-1 uppercase tracking-widest pl-12">
                    {t('subtitle')}
                </p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left: Watchlist */}
                <div className="lg:col-span-3">
                    <Card title={t('watchlist')}>
                        <div className="flex flex-col gap-2">
                            {watchlist.map(item => (
                                <div
                                    key={item.code}
                                    onClick={() => setSelectedFund(item.code)}
                                    className={`group flex items-center justify-between p-3 rounded-md transition-all cursor-pointer ${selectedFund === item.code
                                        ? 'bg-purple-500/20 border border-purple-500/50 text-purple-200'
                                        : 'bg-slate-900/50 border border-slate-800 hover:bg-slate-800 text-slate-400'
                                        }`}
                                >
                                    <div className="flex flex-col overflow-hidden">
                                        <span className="font-bold text-sm truncate pr-2">{item.name || item.code}</span>
                                        <span className="font-mono text-[10px] opacity-60">{item.code}</span>
                                    </div>

                                    <div className="flex items-center gap-2 shrink-0">
                                        {selectedFund === item.code && loading && <RefreshCw className="w-3 h-3 animate-spin" />}
                                        <button
                                            onClick={(e) => handleDelete(e, item.code)}
                                            className="p-1 hover:bg-white/10 rounded-full text-slate-500 hover:text-rose-400 transition-colors"
                                        >
                                            <X className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            ))}

                            <div className="relative mt-2">
                                <input
                                    type="text"
                                    placeholder={t('addPlaceholder')}
                                    className="w-full bg-slate-950 border border-slate-800 rounded-md py-2 pl-3 pr-8 text-sm focus:border-purple-500 outline-none"
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            const val = e.currentTarget.value;
                                            if (val && !watchlist.some(i => i.code === val)) {
                                                setWatchlist([...watchlist, { code: val, name: '' }]);
                                                setSelectedFund(val);
                                                e.currentTarget.value = '';
                                            }
                                        }
                                    }}
                                />
                                <Search className="absolute right-2 top-2.5 w-4 h-4 text-slate-600" />
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Right: Details */}
                <div className="lg:col-span-9">
                    {valuation ? (
                        <div className="flex flex-col gap-6">
                            {/* Main KPI Card */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <Card className="md:col-span-2 relative overflow-hidden bg-gradient-to-br from-slate-900 to-slate-900/50">
                                    <div className="flex flex-col h-full justify-between z-10 relative">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h2 className="text-sm font-mono text-slate-400 uppercase tracking-widest">{t('estimatedGrowth')}</h2>
                                                <div className="text-5xl font-black mt-2 tracking-tighter flex items-center gap-2">
                                                    <span className={valuation.estimated_growth >= 0 ? "text-rose-400" : "text-emerald-400"}>
                                                        {valuation.estimated_growth > 0 ? "+" : ""}{valuation.estimated_growth.toFixed(2)}%
                                                    </span>
                                                </div>
                                            </div>
                                            <Badge variant={valuation.estimated_growth >= 0 ? 'bearish' : 'bullish'}>
                                                {t('live')}
                                            </Badge>
                                        </div>
                                        <div className="mt-4 text-xs text-slate-500 font-mono">
                                            {t('basedOn', { count: valuation.components.length, weight: valuation.total_weight.toFixed(1) })}
                                            <br />
                                            {t('lastUpdated', { time: lastUpdated ? lastUpdated.toLocaleTimeString() : '' })}
                                        </div>
                                    </div>
                                    {/* Background Accents */}
                                    <div className={`absolute -right-10 -top-10 w-40 h-40 blur-3xl opacity-10 rounded-full ${valuation.estimated_growth >= 0 ? 'bg-rose-500' : 'bg-emerald-500'}`}></div>
                                </Card>

                                <Card>
                                    <h2 className="text-sm font-mono text-slate-400 uppercase tracking-widest mb-4">{t('topDrivers')}</h2>
                                    <div className="flex flex-col gap-2">
                                        {valuation.components
                                            .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
                                            .slice(0, 3)
                                            .map(comp => (
                                                <div key={comp.code} className="flex justify-between items-center text-xs border-b border-slate-800/50 pb-2 last:border-0 hover:bg-white/5 p-1 rounded">
                                                    <div className="flex gap-2">
                                                        <span className="font-mono text-slate-500">{comp.code}</span>
                                                        <span className="text-slate-300 truncate max-w-[80px]">{comp.name}</span>
                                                    </div>
                                                    <span className={`font-mono font-bold ${comp.impact >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                                        {comp.impact > 0 ? "+" : ""}{comp.impact.toFixed(3)}%
                                                    </span>
                                                </div>
                                            ))}
                                    </div>
                                </Card>
                            </div>

                            {/* Attribution Table */}
                            <Card title={t('attribution')}>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left border-collapse text-sm">
                                        <thead>
                                            <tr className="border-b border-slate-800 text-slate-500 text-[10px] uppercase tracking-wider">
                                                <th className="p-3">{t('tableStock')}</th>
                                                <th className="p-3 text-right">{t('tablePrice')}</th>
                                                <th className="p-3 text-right">{t('tableChange')}</th>
                                                <th className="p-3 text-right">{t('tableWeight')}</th>
                                                <th className="p-3 text-right">{t('tableImpact')}</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-slate-800/50">
                                            {valuation.components.map(comp => (
                                                <tr key={comp.code} className="group hover:bg-slate-800/30 transition-colors">
                                                    <td className="p-3">
                                                        <div className="flex flex-col">
                                                            <span className="font-bold text-slate-200">{comp.name}</span>
                                                            <span className="text-[10px] font-mono text-slate-500">{comp.code}</span>
                                                        </div>
                                                    </td>
                                                    <td className="p-3 text-right font-mono text-slate-400">
                                                        {comp.price.toFixed(2)}
                                                    </td>
                                                    <td className={`p-3 text-right font-mono font-bold ${comp.change_pct >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                                        {comp.change_pct > 0 ? "+" : ""}{comp.change_pct.toFixed(2)}%
                                                    </td>
                                                    <td className="p-3 text-right font-mono text-slate-500">
                                                        {comp.weight.toFixed(2)}%
                                                    </td>
                                                    <td className={`p-3 text-right font-mono font-bold ${comp.impact >= 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                                                        {comp.impact > 0 ? "+" : ""}{comp.impact.toFixed(3)}%
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </Card>
                        </div>
                    ) : (
                        <div className="h-64 flex items-center justify-center text-slate-500">
                            {loading ? t('loading') : t('selectFund')}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
