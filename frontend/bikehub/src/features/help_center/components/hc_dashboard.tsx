export function HcDashboard() {
    return (
        <div className='space-y-2'>
            <h2 className='text-2xl font-semibold'>数据展示面板</h2>
            <p className='text-muted-foreground text-sm leading-relaxed'>
                这里将展示系统的整体运行概况：实时单车调度状态、站点热力图、警告统计与预测需求曲线等。未来将补充：
                <br />1. 总览卡片：当日任务完成率 / 活跃站点数 / 警告数。
                <br />2. 图表：流量趋势、调度效率、缺车/满桩热力分布。
                <br />3. 交互：通过筛选时间范围、区域、运营分组进行细化分析。
            </p>
        </div>
    )
}

