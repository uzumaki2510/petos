import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Home from '../src/app/page'
import React from 'react'

// Mock fetch
global.fetch = vi.fn()

describe('Foundation Page', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders foundation page headers', () => {
    render(<Home />)
    expect(screen.getByText('PetOS')).toBeTruthy()
    expect(screen.getByText('Phase 2: Engineering Foundation')).toBeTruthy()
  })

  it('renders backend disconnected state on error', async () => {
    (global.fetch as any).mockRejectedValueOnce(new Error('Network error'))
    render(<Home />)
    
    const backendStatus = await screen.findByTestId('backend-status')
    expect(backendStatus.textContent).toContain('Disconnected')
  })
})
