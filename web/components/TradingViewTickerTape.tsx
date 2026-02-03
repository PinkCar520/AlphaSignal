'use client';

import React, { useEffect, useRef, memo } from 'react';

function TradingViewTickerTape() {
    const container = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!container.current) return;

        // Clear previous widget content to prevent duplicates on re-renders
        container.current.innerHTML = '';

        const script = document.createElement("script");
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js";
        script.type = "text/javascript";
        script.async = true;
        script.innerHTML = JSON.stringify({
            "symbols": [
                {
                    "description": "Gold (Spot)",
                    "proName": "OANDA:XAUUSD"
                },
                {
                    "description": "DXY Index",
                    "proName": "TVC:DXY"
                },
                {
                    "description": "US 10Y Yield",
                    "proName": "TVC:US10Y"
                },
                {
                    "description": "Crude Oil (WTI)",
                    "proName": "TVC:USOIL"
                },
                {
                    "description": "VIX Index",
                    "proName": "TVC:VIX"
                },
                {
                    "description": "S&P 500",
                    "proName": "OANDA:SPX500USD"
                }
            ],
            "showSymbolLogo": true,
            "isTransparent": true,
            "displayMode": "adaptive",
            "colorTheme": "dark",
            "locale": "en"
        });

        // Append the standard TradingView wrapper
        const widgetContainer = document.createElement('div');
        widgetContainer.className = "tradingview-widget-container__widget";
        container.current.appendChild(widgetContainer);
        container.current.appendChild(script);

    }, []);

    return (
        <div className="tradingview-widget-container w-full h-12 border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-sm" ref={container}>
            {/* Widget will be injected here */}
        </div>
    );
}

// Memoize to prevent unnecessary re-renders
export default memo(TradingViewTickerTape);
