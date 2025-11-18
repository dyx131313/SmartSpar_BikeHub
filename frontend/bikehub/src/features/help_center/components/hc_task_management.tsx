export function HcTaskManagement() {
    return (
        <div className='space-y-2'>
            <h2 className='text-2xl font-semibold'>调度管理</h2>
            <p className='text-muted-foreground text-sm leading-relaxed'>
                用于管理调度任务的生命周期：创建、分配、执行与核验。未来将补充：
                <br />1. 列表：任务状态（待分配/进行中/已完成/失败）、优先级、关联站点。
                <br />2. 交互：按区域/班组分派任务；支持批量操作与导入导出。
                <br />3. 监控：查看任务执行轨迹与实时进度，异常原因分类汇总。
            </p>
        </div>
    )
}

