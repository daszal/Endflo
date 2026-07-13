import * as React from 'react';

/**
 * Primary interactive control. Pill-shaped, Sora 700, four variants.
 * @startingPoint section="Core" subtitle="Primary pill button, 4 variants" viewport="700x120"
 */
export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'accent';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
}

export function Button(props: ButtonProps): JSX.Element;
