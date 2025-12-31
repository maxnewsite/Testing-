import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface CardProps {
  children: ReactNode
  variant?: 'default' | 'featured' | 'bordered'
  hover?: boolean
  className?: string
  onClick?: () => void
}

export function Card({
  children,
  variant = 'default',
  hover = false,
  className,
  onClick,
}: CardProps) {
  const baseStyles = 'bg-white rounded-2xl transition-all duration-300'

  const variantStyles = {
    default: 'shadow-soft border border-gray-100',
    featured: 'bg-gradient-hero border-2 border-primary-200 shadow-primary relative overflow-hidden',
    bordered: 'border-2 border-gray-200',
  }

  const hoverStyles = hover
    ? 'hover:shadow-lg hover:-translate-y-1 cursor-pointer'
    : ''

  return (
    <div
      className={clsx(baseStyles, variantStyles[variant], hoverStyles, className)}
      onClick={onClick}
    >
      {variant === 'featured' && (
        <div className="absolute top-0 right-0 w-48 h-48 bg-primary-400 rounded-full blur-3xl opacity-10"></div>
      )}
      <div className="relative z-10">{children}</div>
    </div>
  )
}

interface CardHeaderProps {
  children: ReactNode
  className?: string
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={clsx('px-6 py-4 border-b border-gray-100', className)}>
      {children}
    </div>
  )
}

interface CardBodyProps {
  children: ReactNode
  className?: string
}

export function CardBody({ children, className }: CardBodyProps) {
  return (
    <div className={clsx('p-6', className)}>
      {children}
    </div>
  )
}

interface CardFooterProps {
  children: ReactNode
  className?: string
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={clsx('px-6 py-4 border-t border-gray-100', className)}>
      {children}
    </div>
  )
}
