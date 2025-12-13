import { useState, useMemo, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Progress } from "@/components/ui/progress"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Info, Loader2, Play } from 'lucide-react'
import { getPredictionData, getPredictionParams, runPrediction, getPredictionStatus } from '../service'
import {
    useReactTable,
    getCoreRowModel,
    flexRender,
    PaginationState,
    ColumnDef,
} from '@tanstack/react-table'
import { DataTablePagination } from '@/components/data-table'
import { stationTypes } from '../data/data'

const MODELS = ['DLinear', 'TiDE', 'TimesNet']

type PredictionItem = {
    id: string
    time: string
    station_id: number
    station_name: string
    station_type: string
    demand: number
}

export function PredictedDemandView() {
    const [activeModel, setActiveModel] = useState('DLinear')
    const [isDialogOpen, setIsDialogOpen] = useState(false)
    const [selectedModel, setSelectedModel] = useState('DLinear')
    const [targetTime, setTargetTime] = useState('')
    const [polling, setPolling] = useState(false)
    const [progress, setProgress] = useState(0)
    const [statusMessage, setStatusMessage] = useState('')
    const queryClient = useQueryClient()

    const runPredictionMutation = useMutation({
        mutationFn: (data: { model: string, time: string }) => runPrediction(data.model, data.time),
        onSuccess: () => {
            setPolling(true)
        },
    })

    useEffect(() => {
        let interval: NodeJS.Timeout
        if (polling) {
            interval = setInterval(async () => {
                try {
                    const res = await getPredictionStatus(selectedModel)
                    setProgress(res.progress)
                    setStatusMessage(res.message)

                    if (res.status === 'completed' || res.status === 'failed') {
                        setPolling(false)
                        if (res.status === 'completed') {
                            setIsDialogOpen(false)
                            queryClient.invalidateQueries({ queryKey: ['predictionData'] })
                        }
                    }
                } catch (e) {
                    console.error(e)
                    setPolling(false)
                }
            }, 1000)
        }
        return () => clearInterval(interval)
    }, [polling, selectedModel, queryClient])

    const handleRunPrediction = () => {
        setProgress(0)
        setStatusMessage('Starting...')
        runPredictionMutation.mutate({ model: selectedModel, time: targetTime })
    }

    return (
        <div className="space-y-4">
            <Tabs value={activeModel} onValueChange={setActiveModel} className="w-full">
                <div className="flex justify-between items-center mb-4">
                    <TabsList>
                        {MODELS.map((model) => (
                            <TabsTrigger key={model} value={model}>
                                {model}
                            </TabsTrigger>
                        ))}
                    </TabsList>

                    <Dialog open={isDialogOpen} onOpenChange={(open) => {
                        if (!polling) setIsDialogOpen(open)
                    }}>
                        <DialogTrigger asChild>
                            <Button variant="outline" onClick={() => {
                                setSelectedModel(activeModel)
                                setTargetTime('')
                                setProgress(0)
                                setStatusMessage('')
                            }}>
                                <Play className="mr-2 h-4 w-4" />
                                手动预测
                            </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-[425px]">
                            <DialogHeader>
                                <DialogTitle>手动触发预测</DialogTitle>
                                <DialogDescription>
                                    选择模型和目标时间进行即时预测。如果不指定时间，将使用当前系统时间。
                                </DialogDescription>
                            </DialogHeader>
                            <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="model" className="text-right">
                                        模型
                                    </Label>
                                    <Select value={selectedModel} onValueChange={setSelectedModel} disabled={polling}>
                                        <SelectTrigger className="col-span-3">
                                            <SelectValue placeholder="选择模型" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {MODELS.map((m) => (
                                                <SelectItem key={m} value={m}>{m}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="grid grid-cols-4 items-center gap-4">
                                    <Label htmlFor="time" className="text-right">
                                        时间
                                    </Label>
                                    <Input
                                        id="time"
                                        type="datetime-local"
                                        className="col-span-3"
                                        value={targetTime}
                                        onChange={(e) => setTargetTime(e.target.value)}
                                        disabled={polling}
                                    />
                                </div>
                                {polling && (
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span>{statusMessage}</span>
                                            <span>{progress}%</span>
                                        </div>
                                        <Progress value={progress} />
                                    </div>
                                )}
                            </div>
                            <DialogFooter>
                                <Button type="submit" onClick={handleRunPrediction} disabled={runPredictionMutation.isPending || polling}>
                                    {(runPredictionMutation.isPending || polling) && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    {polling ? '预测中...' : '开始预测'}
                                </Button>
                            </DialogFooter>
                        </DialogContent>
                    </Dialog>
                </div>

                {MODELS.map((model) => (
                    <TabsContent key={model} value={model}>
                        <ModelView model={model} />
                    </TabsContent>
                ))}
            </Tabs>
        </div>
    )
}

function ModelView({ model }: { model: string }) {
    const [pagination, setPagination] = useState<PaginationState>({
        pageIndex: 0,
        pageSize: 10,
    })
    const [stationType, setStationType] = useState<string>('all')

    const { data: paramsData } = useQuery({
        queryKey: ['predictionParams', model],
        queryFn: () => getPredictionParams(model),
    })

    const { data: predictionData, isLoading } = useQuery({
        queryKey: ['predictionData', model, pagination.pageIndex, pagination.pageSize, stationType],
        queryFn: () => getPredictionData(model, {
            page: pagination.pageIndex + 1,
            per_page: pagination.pageSize,
            station_type: stationType === 'all' ? undefined : stationType
        }),
    })

    const params = paramsData?.data
    const exists = paramsData?.exists
    const predictions = predictionData?.data || []
    const totalPages = predictionData?.pages || 0

    const columns = useMemo<ColumnDef<PredictionItem>[]>(
        () => [
            {
                accessorKey: 'id',
                header: 'ID',
            },
            {
                accessorKey: 'time',
                header: '时间',
                cell: ({ row }) => row.original.time.replace('T', ' '),
            },
            {
                accessorKey: 'station_id',
                header: '站点ID',
            },
            {
                accessorKey: 'station_name',
                header: '站点名称',
            },
            {
                accessorKey: 'station_type',
                header: '站点类型',
                cell: ({ row }) => {
                    const type = stationTypes.find(
                        (type) => type.value === row.original.station_type
                    )
                    return (
                        <div className="flex items-center">
                            {type?.icon && (
                                <type.icon className="mr-2 h-4 w-4 text-muted-foreground" />
                            )}
                            <span>{type?.label || row.original.station_type}</span>
                        </div>
                    )
                },
            },
            {
                accessorKey: 'demand',
                header: '需求量',
            },
        ],
        []
    )

    const table = useReactTable({
        data: predictions,
        columns,
        pageCount: totalPages,
        state: {
            pagination,
        },
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
    })

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <h3 className="text-lg font-medium">预测结果 ({model})</h3>
                    <Popover>
                        <PopoverTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                                <Info className="h-4 w-4" />
                            </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-80">
                            <div className="grid gap-4">
                                <div className="space-y-2">
                                    <h4 className="font-medium leading-none">模型参数</h4>
                                    <p className="text-sm text-muted-foreground">
                                        {exists ? '模型配置详情' : '未找到该模型的参数信息'}
                                    </p>
                                </div>
                                {exists && (
                                    <div className="grid gap-2 max-h-[300px] overflow-y-auto">
                                        {Object.entries(params).map(([key, value]) => (
                                            <div key={key} className="grid grid-cols-3 items-center gap-4">
                                                <span className="text-sm font-medium">{key}</span>
                                                <span className="col-span-2 text-sm text-muted-foreground break-all">
                                                    {String(value)}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </PopoverContent>
                    </Popover>
                </div>

                <div className="flex items-center gap-2">
                    <Select value={stationType} onValueChange={setStationType}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="筛选站点类型" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">所有类型</SelectItem>
                            {stationTypes.map((type) => (
                                <SelectItem key={type.value} value={type.value}>
                                    <div className="flex items-center">
                                        <type.icon className="mr-2 h-4 w-4" />
                                        <span>{type.label}</span>
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id}>
                                            {header.isPlaceholder
                                                ? null
                                                : flexRender(
                                                    header.column.columnDef.header,
                                                    header.getContext()
                                                )}
                                        </TableHead>
                                    )
                                })}
                            </TableRow>
                        ))}
                    </TableHeader>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    加载中...
                                </TableCell>
                            </TableRow>
                        ) : table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => (
                                <TableRow
                                    key={row.id}
                                    data-state={row.getIsSelected() && 'selected'}
                                >
                                    {row.getVisibleCells().map((cell) => (
                                        <TableCell key={cell.id}>
                                            {flexRender(
                                                cell.column.columnDef.cell,
                                                cell.getContext()
                                            )}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            ))
                        ) : (
                            <TableRow>
                                <TableCell
                                    colSpan={columns.length}
                                    className="h-24 text-center"
                                >
                                    暂无预测数据
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
            <DataTablePagination table={table} />
        </div>
    )
}
