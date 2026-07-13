import React from 'react';

export function Card({ children, padding = '32px', style = {} }) {
  return (
    <div style={{
      background: 'var(--surface-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding,
      ...style,
    }}>
      {children}
    </div>
  );
}
