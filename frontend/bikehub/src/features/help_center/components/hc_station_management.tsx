export function HcStationManagement() {
    return (
        <div className='space-y-2'>
            <h2 className='text-2xl font-semibold'>站点管理</h2>
            <p className='text-muted-foreground text-sm leading-relaxed'>
                此区域用于查看与维护所有站点的状态：库存（车/空桩）、健康指标、运维分级标签等。未来将补充：
                <br />1. 列表与筛选：按行政区域 / 车桩利用率 / 告警等级过滤。
                <br />2. 操作：批量调整阈值、导出站点报表、锁定维护中站点。
                <br />3. 地图：直观呈现缺车与满桩的热点分布。
            </p>
        </div>
    )
}

