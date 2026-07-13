import * as React from 'react';

/**
 * Base surface container — paper background, subtle border, generous radius.
 * @startingPoint section="Core" subtitle="Base surface container" viewport="700x160"
 */
export interface CardProps {
  children: React.ReactNode;
  padding?: string;
  style?: React.CSSProperties;
}

export function Card(props: CardProps): JSX.Element;
