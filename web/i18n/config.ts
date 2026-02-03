export const locales = ['en', 'zh', 'es', 'ar', 'pt', 'ru', 'fr', 'de'] as const;
export type Locale = (typeof locales)[number];

export const localeNames: Record<Locale, string> = {
    en: 'English',
    zh: '中文',
    es: 'Español',
    ar: 'العربية',
    pt: 'Português',
    ru: 'Русский',
    fr: 'Français',
    de: 'Deutsch'
};
