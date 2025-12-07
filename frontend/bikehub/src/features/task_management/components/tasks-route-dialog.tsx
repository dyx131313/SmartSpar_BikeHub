import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { useTasks } from './tasks-provider'
import { useQuery } from '@tanstack/react-query'
import { getRouteForTask } from '../service'
import { Loader2, MapPin, Clock, Route } from 'lucide-react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card } from '@/components/ui/card'

export function TasksRouteDialog() {
  const { open, setOpen, currentRow } = useTasks()
  const isOpen = open === 'view-route'

  const { data: routeData, isLoading, error } = useQuery({
    queryKey: ['route', currentRow?.id],
    queryFn: () => currentRow ? getRouteForTask(currentRow.id) : Promise.resolve(null),
    enabled: isOpen && !!currentRow,
  })

  const route = routeData?.data?.calculated_route || routeData?.data?.path_data

  return (
    <Dialog open={isOpen} onOpenChange={(v) => !v && setOpen(null)}>
      <DialogContent className='sm:max-w-[600px]'>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Route className="h-5 w-5" />
            任务路线规划
          </DialogTitle>
          <DialogDescription>
            任务: {currentRow?.task_name} (ID: {currentRow?.id})
          </DialogDescription>
        </DialogHeader>

        <div className='py-4'>
          {isLoading ? (
            <div className='flex flex-col items-center justify-center p-8 text-muted-foreground gap-2'>
              <Loader2 className='h-8 w-8 animate-spin' />
              <p>正在计算最优路径...</p>
            </div>
          ) : error ? (
            <div className='p-4 rounded-md bg-destructive/10 text-destructive'>
              无法获取路线信息: {(error as any).message}
            </div>
          ) : route ? (
            <div className='space-y-6'>
              <div className='grid grid-cols-2 gap-4'>
                <Card className='p-4 flex flex-col items-center justify-center bg-muted/30'>
                  <span className='text-sm text-muted-foreground flex items-center gap-1 mb-1'>
                    <MapPin className="h-3 w-3" /> 总距离
                  </span>
                  <span className='text-2xl font-bold'>{route.total_distance} <span className="text-sm font-normal">米</span></span>
                </Card>
                <Card className='p-4 flex flex-col items-center justify-center bg-muted/30'>
                  <span className='text-sm text-muted-foreground flex items-center gap-1 mb-1'>
                    <Clock className="h-3 w-3" /> 预计时间
                  </span>
                  <span className='text-2xl font-bold'>{route.estimated_time} <span className="text-sm font-normal">分钟</span></span>
                </Card>
              </div>
              
              <div className="border rounded-md">
                <div className="bg-muted/50 px-4 py-2 border-b text-sm font-medium">
                  推荐路径节点序列
                </div>
                <ScrollArea className='h-[250px] p-4'>
                  <div className='relative pl-4 ml-2 border-l-2 border-muted space-y-6'>
                    {route.path?.map((node: number, index: number) => (
                      <div key={index} className='relative'>
                        <div className={`absolute -left-[23px] top-0 w-4 h-4 rounded-full border-2 border-background ${
                          index === 0 ? 'bg-green-500' : 
                          index === route.path.length - 1 ? 'bg-red-500' : 'bg-primary'
                        }`} />
                        <div className="flex flex-col">
                          <span className="text-sm font-medium flex items-center gap-2">
                            站点 ID: {node}
                            {index === 0 && <span className='text-[10px] bg-green-100 text-green-800 px-1.5 py-0.5 rounded-full'>起点</span>}
                            {index === route.path.length - 1 && <span className='text-[10px] bg-red-100 text-red-800 px-1.5 py-0.5 rounded-full'>终点</span>}
                          </span>
                          {index < route.path.length - 1 && (
                            <span className="text-xs text-muted-foreground mt-1">
                              ↓ 前往下一站
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          ) : (
            <div className="text-center text-muted-foreground p-8">
              暂无路线数据
            </div>
          )}
        </div>

        <DialogFooter>
          <Button onClick={() => setOpen(null)}>关闭</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

