import React from 'react';

const base = {
  fontFamily: 'var(--font-body)',
  fontWeight: 700,
  border: 'none',
  borderRadius: 'var(--radius-pill)',
  cursor: 'pointer',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '8px',
  transition: 'opacity 0.15s ease, transform 0.05s ease',
};

const sizes = {
  sm: { fontSize: '13px', padding: '8px 16px' },
  md: { fontSize: '15px', padding: '11px 22px' },
  lg: { fontSize: '17px', padding: '14px 28px' },
};

const variants = {
  primary: { background: 'var(--ink)', color: 'var(--paper)' },
  secondary: { background: 'transparent', color: 'var(--ink)', boxShadow: 'inset 0 0 0 1.5px var(--ink)' },
  ghost: { background: 'transparent', color: 'var(--ink)' },
  accent: { background: 'var(--accent-indigo)', color: '#fff' },
};

export function Button({ children, variant = 'primary', size = 'md', disabled = false, onClick, ...props }) {
  const style = {
    ...base,
    ...sizes[size],
    ...variants[variant],
    opacity: disabled ? 0.4 : 1,
    cursor: disabled ? 'not-allowed' : 'pointer',
  };
  return (
    <button style={style} disabled={disabled} onClick={onClick} {...props}
      onMouseDown={(e) => { if (!disabled) e.currentTarget.style.opacity = '0.75'; }}
      onMouseUp={(e) => { if (!disabled) e.currentTarget.style.opacity = '1'; }}
      onMouseLeave={(e) => { if (!disabled) e.currentTarget.style.opacity = '1'; }}
    >
      {children}
    </button>
  );
}
