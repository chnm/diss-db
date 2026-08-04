/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                paper:  'var(--paper)',
                paper2: 'var(--paper2)',
                paper3: 'var(--paper3)',
                ink:    'var(--ink)',
                ink2:   'var(--ink2)',
                mute:   'var(--mute)',
                line:   'var(--line)',
                line2:  'var(--line2)',
                accent: 'var(--accent)',
                avatar: 'var(--avatar)',
            },
            fontFamily: {
                serif: ['"EB Garamond"', '"Source Serif 4"', 'Georgia', 'serif'],
                sans:  ['"Source Sans 3"', '-apple-system', 'sans-serif'],
                mono:  ['"JetBrains Mono"', 'ui-monospace', 'Menlo', 'monospace'],
            },
            fontSize: {
                'display-xl': ['60px', { lineHeight: '1.05', letterSpacing: '-1.2px', fontWeight: '500' }],
                'display-lg': ['48px', { lineHeight: '1.1', letterSpacing: '-0.6px', fontWeight: '500' }],
                'display-md': ['38px', { lineHeight: '1.1', letterSpacing: '-0.5px', fontWeight: '500' }],
                'display-sm': ['30px', { lineHeight: '1.2', letterSpacing: '-0.4px', fontWeight: '500' }],
                'heading':    ['28px', { lineHeight: '1.2', letterSpacing: '-0.3px', fontWeight: '500' }],
                'title-lg':   ['22px', { lineHeight: '1.25', letterSpacing: '-0.2px', fontWeight: '500' }],
                'title':      ['19px', { lineHeight: '1.3', fontWeight: '500' }],
                'body-lg':    ['19px', { lineHeight: '1.65' }],
                'body':       ['15px', { lineHeight: '1.55' }],
                'meta':       ['13px', { lineHeight: '1.4' }],
                'meta-sm':    ['11px', { lineHeight: '1.4' }],
            },
            spacing: {
                'page': '64px',
                'page-tablet': '24px',
                'page-mobile': '16px',
                '18': '4.5rem',
                '22': '5.5rem',
            },
            borderRadius: {
                none: '0',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
