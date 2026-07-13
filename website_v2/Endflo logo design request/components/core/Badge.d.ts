import * as React from 'react';

/**
 * Small status/label pill in Space Mono, uppercase, wide tracking.
 * @startingPoint section="Core" subtitle="Status pill, 6 tones" viewport="700x90"
 */
export interface BadgeProps {
  children: React.ReactNode;
  tone?: 'neutral' | 'ink' | 'indigo' | 'amber' | 'success' | 'danger';
}

export function Badge(props: BadgeProps): JSX.Element;
