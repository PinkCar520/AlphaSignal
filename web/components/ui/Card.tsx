import React from 'react';

interface CardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'title'> {
  title?: React.ReactNode;
  action?: React.ReactNode;
  contentClassName?: string;
}

export function Card({ className = '', title, action, children, contentClassName, ...props }: CardProps) {
  const baseClasses = "bg-white rounded-xl overflow-hidden shadow-sm border border-slate-200 transition-all duration-300 hover:shadow-md";
  const combinedClasses = `${baseClasses} ${className}`.trim();

  return (
    <div
      className={combinedClasses}
      {...props}
    >
      {(title || action) && (
        <div className="px-5 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          {title && <div className="font-semibold text-slate-800 tracking-tight">{title}</div>}
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={contentClassName || "p-5"}>
        {children}
      </div>
    </div>
  );
}
