export const faqs = [
    {
        id: 'dispatch-logic',
        question: '系统如何分配调度任务？',
        answer: '平台依据站点实时空余车桩、单车存量、预测需求曲线与地理距离动态生成调度任务。'
    },
    {
        id: 'low-stock',
        question: '如何识别低车量站点？',
        answer: '低于设定阈值（可在设置里自定义）的站点会进入预警列表，并触发补车建议。'
    },
    {
        id: 'high-load',
        question: '高峰期如何优化调度？',
        answer: '结合历史出行模式与天气事件进行需求预测，提前分配运力。'
    },
]