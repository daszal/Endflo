import React from 'react';

const tones = {
  neutral: { background: 'var(--mist)', color: 'var(--ink)' },
  ink: { background: 'var(--ink)', color: 'var(--paper)' },
  indigo: { background: 'var(--accent-indigo)', color: '#fff' },
  amber: { background: 'var(--accent-amber)', color: '#fff' },
  success: { background: 'var(--success)', color: '#fff' },
  danger: { background: 'var(--danger)', color: '#fff' },
};

export function Badge({ children, tone = 'neutral' }) {
  return (
    <span style={{
      fontFamily: 'var(--font-mono)',
      fontWeight: 700,
      fontSize: '12px',
      letterSpacing: 'var(--tracking-mono-label)',
      textTransform: 'uppercase',
      padding: '6px 12px',
      borderRadius: 'var(--radius-pill)',
      display: 'inline-flex',
      ...tones[tone],
    }}>
      {children}
    </span>
  );
}
