# PeopleSay Design System

## Brand Identity

### Logo Concept
**PeopleSay** - A platform where people's voices matter

Tagline: "Your Opinion, Amplified"

### Brand Values
- **Authentic**: Real people, real opinions
- **Empowering**: Every voice counts
- **Trustworthy**: Quality insights you can rely on
- **Accessible**: Simple, intuitive, inclusive

## Color Palette

### Primary Colors
```
Primary Blue:    #2563EB (rgb(37, 99, 235))
Primary Dark:    #1E40AF (rgb(30, 64, 175))
Primary Light:   #3B82F6 (rgb(59, 130, 246))
Primary Lighter: #93C5FD (rgb(147, 197, 253))
```

### Secondary Colors
```
Accent Purple:   #7C3AED (rgb(124, 58, 237))
Accent Green:    #10B981 (rgb(16, 185, 129))
Accent Orange:   #F59E0B (rgb(245, 158, 11))
Accent Pink:     #EC4899 (rgb(236, 72, 153))
```

### Neutral Colors
```
Gray 50:   #F9FAFB
Gray 100:  #F3F4F6
Gray 200:  #E5E7EB
Gray 300:  #D1D5DB
Gray 400:  #9CA3AF
Gray 500:  #6B7280
Gray 600:  #4B5563
Gray 700:  #374151
Gray 800:  #1F2937
Gray 900:  #111827
```

### Semantic Colors
```
Success:  #10B981 (Green)
Warning:  #F59E0B (Orange)
Error:    #EF4444 (Red)
Info:     #3B82F6 (Blue)
```

## Typography

### Font Families
```css
/* Primary Font - Headings */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Secondary Font - Body */
font-family: 'Inter', system-ui, sans-serif;

/* Monospace - Code */
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

### Type Scale
```
Hero:        72px / 4.5rem   (font-weight: 800)
H1:          48px / 3rem     (font-weight: 700)
H2:          36px / 2.25rem  (font-weight: 700)
H3:          30px / 1.875rem (font-weight: 600)
H4:          24px / 1.5rem   (font-weight: 600)
H5:          20px / 1.25rem  (font-weight: 600)
H6:          18px / 1.125rem (font-weight: 600)

Body Large:  18px / 1.125rem (font-weight: 400)
Body:        16px / 1rem     (font-weight: 400)
Body Small:  14px / 0.875rem (font-weight: 400)
Caption:     12px / 0.75rem  (font-weight: 400)
```

### Line Heights
```
Tight:   1.25
Normal:  1.5
Relaxed: 1.75
Loose:   2
```

## Spacing System

### Scale (8px base)
```
xs:  4px  (0.25rem)
sm:  8px  (0.5rem)
md:  16px (1rem)
lg:  24px (1.5rem)
xl:  32px (2rem)
2xl: 48px (3rem)
3xl: 64px (4rem)
4xl: 96px (6rem)
```

### Component Spacing
```
Padding Small:    8px 16px
Padding Medium:   12px 24px
Padding Large:    16px 32px

Margin Small:     8px
Margin Medium:    16px
Margin Large:     24px
```

## Border Radius

```
None:   0px
sm:     4px
md:     8px
lg:     12px
xl:     16px
2xl:    24px
full:   9999px
```

## Shadows

```css
/* Small */
box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);

/* Medium */
box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1),
            0 2px 4px -2px rgb(0 0 0 / 0.1);

/* Large */
box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1),
            0 4px 6px -4px rgb(0 0 0 / 0.1);

/* XL */
box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1),
            0 8px 10px -6px rgb(0 0 0 / 0.1);

/* Colored (Primary) */
box-shadow: 0 10px 25px -5px rgb(37 99 235 / 0.3);
```

## Components

### Buttons

#### Primary Button
```css
background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
color: white;
padding: 12px 24px;
border-radius: 8px;
font-weight: 600;
box-shadow: 0 4px 6px -1px rgb(37 99 235 / 0.3);
transition: all 0.2s;

&:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 15px -3px rgb(37 99 235 / 0.4);
}
```

#### Secondary Button
```css
background: white;
color: #2563EB;
border: 2px solid #2563EB;
padding: 12px 24px;
border-radius: 8px;
font-weight: 600;

&:hover {
  background: #EFF6FF;
}
```

#### Ghost Button
```css
background: transparent;
color: #2563EB;
padding: 12px 24px;
border-radius: 8px;

&:hover {
  background: #F3F4F6;
}
```

### Cards

#### Standard Card
```css
background: white;
border-radius: 12px;
padding: 24px;
box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
border: 1px solid #E5E7EB;

&:hover {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  transform: translateY(-2px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
```

#### Featured Card
```css
background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
border-radius: 16px;
padding: 32px;
border: 2px solid #93C5FD;
position: relative;
overflow: hidden;

&::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, #3B82F6 0%, transparent 70%);
  opacity: 0.1;
}
```

### Inputs

#### Text Input
```css
background: white;
border: 2px solid #E5E7EB;
border-radius: 8px;
padding: 12px 16px;
font-size: 16px;
transition: all 0.2s;

&:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
  outline: none;
}

&::placeholder {
  color: #9CA3AF;
}
```

### Badges

```css
/* Status Badge */
.badge {
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-success {
  background: #D1FAE5;
  color: #065F46;
}

.badge-warning {
  background: #FEF3C7;
  color: #92400E;
}

.badge-error {
  background: #FEE2E2;
  color: #991B1B;
}
```

## Layout Patterns

### Container
```css
max-width: 1280px;
margin: 0 auto;
padding: 0 24px;
```

### Grid System
```css
/* 12-column grid */
display: grid;
grid-template-columns: repeat(12, 1fr);
gap: 24px;

/* Responsive columns */
@media (max-width: 768px) {
  grid-template-columns: 1fr;
}
```

### Section Spacing
```css
padding-top: 96px;
padding-bottom: 96px;

@media (max-width: 768px) {
  padding-top: 48px;
  padding-bottom: 48px;
}
```

## Animations

### Transitions
```css
/* Standard */
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

/* Smooth */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Bouncy */
transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Keyframes
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

## Iconography

### Icon Style
- Line-based icons (2px stroke)
- 24x24px default size
- Rounded caps and joins
- Consistent visual weight

### Recommended Icon Sets
- Lucide Icons (primary)
- Heroicons
- Feather Icons

## Accessibility

### Color Contrast
- Text on white background: minimum 4.5:1
- Large text (18px+): minimum 3:1
- Interactive elements: minimum 3:1

### Focus States
```css
:focus-visible {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}
```

### Screen Reader Support
- Use semantic HTML
- Include aria-labels
- Provide text alternatives for images

## Responsive Breakpoints

```css
/* Mobile First */
sm:  640px   /* Small tablets */
md:  768px   /* Tablets */
lg:  1024px  /* Laptops */
xl:  1280px  /* Desktops */
2xl: 1536px  /* Large screens */
```

## Dark Mode Support

### Dark Theme Colors
```
Background:     #111827
Surface:        #1F2937
Surface Light:  #374151
Text Primary:   #F9FAFB
Text Secondary: #D1D5DB
Border:         #4B5563
```

## Usage Guidelines

### Do's
✓ Use consistent spacing from the scale
✓ Maintain hierarchy with typography
✓ Use semantic colors appropriately
✓ Keep layouts clean and uncluttered
✓ Provide clear feedback for interactions

### Don'ts
✗ Mix multiple color palettes
✗ Use arbitrary spacing values
✗ Overuse animations
✗ Ignore responsive design
✗ Compromise accessibility

## Implementation

### Tailwind Config
See `frontend/tailwind.config.ts` for complete theme configuration

### CSS Variables
```css
:root {
  --color-primary: #2563EB;
  --color-primary-dark: #1E40AF;
  --color-primary-light: #3B82F6;
  --spacing-unit: 8px;
  --border-radius: 8px;
  --font-sans: 'Inter', sans-serif;
}
```

## Resources

- Design Tool: Figma
- Icon Library: Lucide Icons
- Font: Inter (Google Fonts)
- Illustrations: unDraw, Storyset
- Color Tool: Coolors.co
