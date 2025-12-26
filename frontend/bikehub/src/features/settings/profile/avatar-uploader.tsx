import { useState, useCallback } from 'react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { apiPut, apiPost, apiDelete, buildStaticUrl } from '@/lib/api'
import { Camera, Upload, Trash2, X } from 'lucide-react'
import { getInitials } from '@/lib/utils'

interface AvatarUploaderProps {
  avatarUrl?: string
  fullName?: string
  onAvatarChange?: (newUrl: string) => void
}

interface AvatarDialogProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onAvatarChange: (newUrl: string) => void
}

function AvatarDialog({ isOpen, onOpenChange, onAvatarChange }: AvatarDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [isUploading, setIsUploading] = useState(false)

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        toast.error('请选择图片文件')
        return
      }

      // 验证文件大小（5MB）
      if (file.size > 2 * 1024 * 1024) {
        toast.error('图片大小不能超过2MB')
        return
      }

      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = (e) => setPreviewUrl(e.target?.result as string)
      reader.readAsDataURL(file)
    }
  }, [])

  const handleUpload = useCallback(async () => {
    if (!selectedFile) {
      toast.error('请选择要上传的图片')
      return
    }

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('avatar', selectedFile)

      console.log('DEBUG: FormData created:', formData)
      console.log('DEBUG: FormData keys:', Array.from(formData.keys()))
      console.log('DEBUG: FormData avatar:', formData.get('avatar'))

      const response = await apiPost('/api/users/avatar', formData)

      if (response.data?.avatar_url) {
        toast.success('头像上传成功')
        onAvatarChange?.(response.data.avatar_url)
        onOpenChange(false)
        setSelectedFile(null)
        setPreviewUrl('')
      } else {
        toast.error('头像上传失败')
      }
    } catch (error: any) {
      console.error('Avatar upload error:', error)
      toast.error(error.message || '头像上传失败，请重试')
    } finally {
      setIsUploading(false)
    }
  }, [selectedFile, onAvatarChange, onOpenChange])

  const handleDelete = useCallback(async () => {
    try {
      await apiDelete('/api/users/avatar')
      toast.success('头像已删除')
      onAvatarChange?.('')
      onOpenChange(false)
    } catch (error: any) {
      console.error('Avatar delete error:', error)
      toast.error(error.message || '删除失败，请重试')
    }
  }, [onAvatarChange, onOpenChange])

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>设置头像</DialogTitle>
          <DialogDescription>
            上传一张 JPG、PNG 格式的图片作为头像。图片大小不能超过 2MB。
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col items-center gap-4 py-4">
          <div className="relative">
            <Avatar className="w-32 h-32">
              {previewUrl ? (
                <AvatarImage src={previewUrl} alt="预览" />
              ) : (
                <AvatarFallback className="text-2xl">
                  {getInitials('Preview')}
                </AvatarFallback>
              )}
            </Avatar>
            {selectedFile && (
              <Button
                type="button"
                variant="destructive"
                size="icon"
                className="absolute -top-2 -right-2 h-8 w-8"
                onClick={() => {
                  setSelectedFile(null)
                  setPreviewUrl('')
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
          <div className="w-full space-y-4">
            <div className="space-y-2">
              <Label htmlFor="avatar">选择图片</Label>
              <Input
                id="avatar"
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                disabled={isUploading}
              />
            </div>
            {selectedFile && (
              <div className="flex items-center justify-between p-2 bg-muted rounded-md">
                <span className="text-sm truncate">{selectedFile.name}</span>
                <span className="text-xs text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </span>
              </div>
            )}
          </div>
        </div>
        <DialogFooter className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => handleDelete()}
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            删除头像
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              取消
            </Button>
            <Button onClick={handleUpload} disabled={isUploading || !selectedFile}>
              {isUploading ? '上传中...' : '上传'}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export function AvatarUploader({ avatarUrl, fullName, onAvatarChange }: AvatarUploaderProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  return (
    <Card>
      <CardHeader className="text-center pb-4">
        <CardTitle className="text-2xl font-bold">个人头像</CardTitle>
        <CardDescription>
          点击头像可以更换或删除你的个人头像
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-6">
        <div className="relative group cursor-pointer" onClick={() => setIsDialogOpen(true)}>
          <Avatar className="w-24 h-24 ring-4 ring-primary/20 ring-offset-2 transition-all duration-200 group-hover:ring-primary/40 group-hover:scale-105">
            {avatarUrl ? (
              <>
              {console.log('当前渲染的头像 URL:', buildStaticUrl(avatarUrl))}
              <AvatarImage
                src={buildStaticUrl(avatarUrl)}
                alt={fullName || '用户头像'}
                className="object-cover"
                onError={(e) => {
                  console.error('图片加载失败，地址为:', e.currentTarget.src);
                }}
                
                onLoad={() => console.log('Avatar image loaded successfully:', avatarUrl)}
              />
              </>
            ) : (
              <AvatarFallback className="text-2xl bg-gradient-to-br from-primary/20 to-primary/10">
                {getInitials(fullName)}
              </AvatarFallback>
            )}
          </Avatar>
          <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <Camera className="h-8 w-8 text-white" />
          </div>
        </div>

        <Button
          onClick={() => setIsDialogOpen(true)}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Upload className="h-4 w-4" />
          更换头像
        </Button>

        <AvatarDialog
          isOpen={isDialogOpen}
          onOpenChange={setIsDialogOpen}
          onAvatarChange={(newUrl) => {
            onAvatarChange?.(newUrl)
          }}
        />
      </CardContent>
    </Card>
  )
}