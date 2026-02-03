import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  action?: React.ReactNode;
}

export function Card({ className = '', title, action, children, ...props }: CardProps) {
  const baseClasses = "glass-panel rounded-xl overflow-hidden shadow-xl transition-all duration-300 hover:shadow-2xl hover:border-slate-700/80";
  const combinedClasses = `${baseClasses} ${className}`.trim();

  return (
    <div
      className={combinedClasses}
      {...props}
    >
      {(title || action) && (
        <div className="px-5 py-4 border-b border-slate-800/60 flex justify-between items-center bg-slate-900/30">
          {title && <h3 className="font-semibold text-slate-200 tracking-tight">{title}</h3>}
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="p-5">
        {children}
      </div>
    </div>
  );
}
