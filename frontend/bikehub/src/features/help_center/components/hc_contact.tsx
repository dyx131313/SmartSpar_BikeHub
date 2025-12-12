import { Mail, MessageSquare, Github } from 'lucide-react'
import { Link } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { useFeedback } from '@/features/feedback/components/feedback-provider'

export function HcContact() {
    const feedback = useFeedback()
    return (
        <div className='space-y-3'>
            <h2 className='text-2xl font-semibold'>联系我们</h2>
            <p className='text-sm text-muted-foreground leading-relaxed'>
                如需反馈问题、提交建议或与开发者沟通，请通过以下方式联系我们。
                本段为占位说明，可在后续替换为实际的联系方式与表单入口。
            </p>

            <ul className='space-y-2'>
                <li className='flex items-center gap-2'>
                    <Mail className='size-4' />
                    <span className='text-sm'>邮箱：support@example.com</span>
                </li>
                <li className='flex items-center gap-2'>
                    <MessageSquare className='size-4' />
                    <span className='text-sm'>工单/讨论：请在项目的讨论区或工单系统提交</span>
                </li>
                <li className='flex items-center gap-2'>
                    <Github className='size-4' />
                    <span className='text-sm'>GitHub：稍后补充仓库地址</span>
                </li>
            </ul>

            <div className='rounded-md border p-4 text-sm text-muted-foreground'>
                温馨提示：请尽可能附上问题复现步骤、截图/录屏、期望结果与实际结果，
                以及浏览器控制台报错信息，这将帮助我们更快分析与处理。
            </div>

            <div className='pt-4'>
                <Button onClick={() => feedback.setOpen('create')}>提交反馈</Button>
            </div>
        </div>
    )
}

export default HcContact
