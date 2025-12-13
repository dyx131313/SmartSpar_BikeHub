import React, { createContext, useContext, useRef, useState } from 'react'
import { ConfirmDialog } from './confirm-dialog'

type ConfirmOptions = {
  title?: React.ReactNode
  desc?: React.ReactNode
  confirmText?: React.ReactNode
  cancelBtnText?: string
  destructive?: boolean
}

type ConfirmCtx = {
  confirm: (opts: ConfirmOptions) => Promise<boolean>
}

const ConfirmContext = createContext<ConfirmCtx | null>(null)

export function ConfirmProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  const [opts, setOpts] = useState<ConfirmOptions>({})
  const resolver = useRef<(v: boolean) => void | null>(null)

  const confirm = (options: ConfirmOptions) => {
    setOpts(options)
    setOpen(true)
    return new Promise<boolean>((resolve) => {
      resolver.current = resolve
    })
  }

  const handleConfirm = () => {
    setOpen(false)
    resolver.current?.(true)
    resolver.current = null
  }

  const handleCancel = () => {
    setOpen(false)
    resolver.current?.(false)
    resolver.current = null
  }

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      <ConfirmDialog
        open={open}
        onOpenChange={(v) => {
          if (!v) handleCancel()
          setOpen(v)
        }}
        title={opts.title ?? '确认'}
        desc={opts.desc ?? ''}
        confirmText={opts.confirmText ?? '确认'}
        cancelBtnText={opts.cancelBtnText ?? '取消'}
        destructive={opts.destructive}
        handleConfirm={handleConfirm}
      />
    </ConfirmContext.Provider>
  )
}

export function useConfirm() {
  const ctx = useContext(ConfirmContext)
  if (!ctx) throw new Error('useConfirm must be used within ConfirmProvider')
  return ctx.confirm
}

export default ConfirmProvider
