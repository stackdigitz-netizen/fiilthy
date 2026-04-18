import React from 'react';
import './BrandLogo.css';

function BrandMark() {
  return (
    <svg className="brand-logo__mark" viewBox="0 0 188 210" role="img" aria-hidden="true">
      <defs>
        <linearGradient id="fiilthy-mark-line" x1="16" y1="192" x2="168" y2="22" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#8f6b14" />
          <stop offset="0.48" stopColor="#d4af37" />
          <stop offset="1" stopColor="#f4dd91" />
        </linearGradient>
        <linearGradient id="fiilthy-mark-fill" x1="38" y1="166" x2="152" y2="38" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#b88924" stopOpacity="0.22" />
          <stop offset="1" stopColor="#f4dd91" stopOpacity="0.08" />
        </linearGradient>
        <filter id="fiilthy-mark-glow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="3.2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <path
        d="M31 186 L79 36 H171 L147 58 H94 L67 110 H121 L31 186 Z"
        fill="url(#fiilthy-mark-fill)"
        opacity="0.95"
      />
      <path
        d="M31 186 L79 36 H171 L147 58 H94 L67 110 H121 L31 186 Z"
        fill="none"
        stroke="url(#fiilthy-mark-line)"
        strokeWidth="7"
        strokeLinejoin="round"
        strokeLinecap="round"
        filter="url(#fiilthy-mark-glow)"
      />
      <path
        d="M59 146 L92 74 H145"
        fill="none"
        stroke="url(#fiilthy-mark-line)"
        strokeWidth="10"
        strokeLinejoin="round"
        strokeLinecap="square"
        opacity="0.9"
      />
      <path
        d="M34 36 V102"
        fill="none"
        stroke="url(#fiilthy-mark-line)"
        strokeWidth="5.5"
        strokeLinecap="round"
        filter="url(#fiilthy-mark-glow)"
      />
      <path
        d="M52 44 V82 L70 64"
        fill="none"
        stroke="url(#fiilthy-mark-line)"
        strokeWidth="5.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        filter="url(#fiilthy-mark-glow)"
      />
      <path
        d="M28 112 H50 L62 98"
        fill="none"
        stroke="url(#fiilthy-mark-line)"
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
        filter="url(#fiilthy-mark-glow)"
      />
      <circle cx="34" cy="36" r="8" fill="#f4dd91" filter="url(#fiilthy-mark-glow)" />
      <circle cx="34" cy="57" r="6.5" fill="#d4af37" filter="url(#fiilthy-mark-glow)" />
      <circle cx="34" cy="112" r="6.5" fill="#f8f4ea" filter="url(#fiilthy-mark-glow)" />
      <circle cx="53" cy="44" r="6.5" fill="#f4dd91" filter="url(#fiilthy-mark-glow)" />
      <circle cx="53" cy="82" r="6" fill="#d4af37" filter="url(#fiilthy-mark-glow)" />
      <circle cx="28" cy="112" r="6" fill="#f8f4ea" filter="url(#fiilthy-mark-glow)" />
      <ellipse cx="36" cy="196" rx="28" ry="7" fill="rgba(212, 175, 55, 0.5)" filter="url(#fiilthy-mark-glow)" />
    </svg>
  );
}

export default function BrandLogo({
  variant = 'full',
  theme = 'light',
  size = 'md',
  className = '',
  style,
}) {
  const classes = [
    'brand-logo',
    `brand-logo--${variant}`,
    `brand-logo--${theme}`,
    `brand-logo--${size}`,
    className,
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} style={style} aria-label="Fiilthy logo">
      <BrandMark />
      {variant === 'full' && (
        <>
          <div className="brand-logo__copy">
            <span className="brand-logo__wordmark">
              <span className="brand-logo__main">FiiLTHY</span>
              <span className="brand-logo__suffix">.Ai</span>
            </span>
          </div>
          <span className="brand-logo__line" aria-hidden="true" />
        </>
      )}
    </div>
  );
}