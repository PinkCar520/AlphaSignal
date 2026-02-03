'use client';

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from '@/i18n/navigation';
import { ChangeEvent, useTransition } from 'react';
import { Globe, Check } from 'lucide-react';
import { locales, localeNames } from '@/i18n/config';

export default function LanguageSwitcher() {
    const locale = useLocale();
    const router = useRouter();
    const pathname = usePathname();
    const [isPending, startTransition] = useTransition();

    const onSelectChange = (e: ChangeEvent<HTMLSelectElement>) => {
        const nextLocale = e.target.value;
        startTransition(() => {
            router.replace(pathname, { locale: nextLocale });
        });
    };

    return (
        <div className="relative group">
            <div className="flex items-center gap-2 bg-slate-900 border border-slate-700/50 rounded-lg px-3 py-1.5 hover:border-emerald-500/50 transition-colors">
                <Globe className="w-3 h-3 text-emerald-500" />
                <select
                    defaultValue={locale}
                    disabled={isPending}
                    onChange={onSelectChange}
                    className="bg-transparent text-xs text-slate-300 font-mono focus:outline-none appearance-none cursor-pointer pr-4"
                    style={{
                        backgroundImage: "none"
                    }}
                >
                    {locales.map((cur) => (
                        <option key={cur} value={cur} className="bg-slate-900 text-slate-300">
                            {localeNames[cur as keyof typeof localeNames]}
                        </option>
                    ))}
                </select>
                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[8px] text-slate-500">
                    ▼
                </div>
            </div>
        </div>
    );
}
