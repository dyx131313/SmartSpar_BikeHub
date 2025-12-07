import React, { useState } from 'react'
import useDialogState from '@/hooks/use-dialog-state'
import { type Demand } from '../data/schema'

type DemandDialogType = 'create' | 'update' | 'delete' | 'import'

type DemandContextType = {
  open: DemandDialogType | null
  setOpen: (str: DemandDialogType | null) => void
  currentRow: Demand | null
  setCurrentRow: React.Dispatch<React.SetStateAction<Demand | null>>
}

const DemandContext = React.createContext<DemandContextType | null>(null)

export function DemandProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useDialogState<DemandDialogType>(null)
  const [currentRow, setCurrentRow] = useState<Demand | null>(null)

  return (
    <DemandContext value={{ open, setOpen, currentRow, setCurrentRow }}>
      {children}
    </DemandContext>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useDemand = () => {
  const demandContext = React.useContext(DemandContext)

  if (!demandContext) {
    throw new Error('useDemand has to be used within <DemandContext>')
  }

  return demandContext
}
