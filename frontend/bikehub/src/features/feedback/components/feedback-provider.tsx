import { createContext, useContext, useState, ReactNode } from 'react'
import { Feedback } from '../data/schema'

interface FeedbackContextType {
  open: string | null
  setOpen: (str: string | null) => void
  currentRow: Feedback | null
  setCurrentRow: (row: Feedback | null) => void
}

const FeedbackContext = createContext<FeedbackContextType | null>(null)

interface Props {
  children: ReactNode
}

export function FeedbackProvider({ children }: Props) {
  const [open, setOpen] = useState<string | null>(null)
  const [currentRow, setCurrentRow] = useState<Feedback | null>(null)

  return (
    <FeedbackContext.Provider value={{ open, setOpen, currentRow, setCurrentRow }}>
      {children}
    </FeedbackContext.Provider>
  )
}

export function useFeedback() {
  const context = useContext(FeedbackContext)
  if (!context) {
    throw new Error('useFeedback must be used within a FeedbackProvider')
  }
  return context
}



