import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { HcDashboard } from './components/hc_dashboard'
import { HcStationManagement } from './components/hc_station_management'
import { HcTaskManagement } from './components/hc_task_management'
import { SearchBox } from './components/search_box'
import { FaqList } from './components/faq_list'
import { HcContact } from './components/hc_contact.tsx'

export function HelpCenter() {
    const [query, setQuery] = useState('')

    return (
        <div className='space-y-8 p-6'>
            <header className='space-y-2'>
                <h1 className='text-3xl font-bold'>帮助中心</h1>
                <p className='text-muted-foreground'>
                    智能共享单车调度系统的使用说明与常见问题。
                </p>
            </header>

            <Tabs defaultValue='docs' className='space-y-4'>
                <TabsList>
                    <TabsTrigger value='docs'>帮助文档</TabsTrigger>
                    <TabsTrigger value='faq'>常见FAQ</TabsTrigger>
                    <TabsTrigger value='contact'>联系我们</TabsTrigger>
                </TabsList>

                <TabsContent value='docs' className='space-y-6'>
                    <section id='dashboard' className='space-y-4'>
                        <HcDashboard />
                    </section>
                    <section id='station' className='space-y-4'>
                        <HcStationManagement />
                    </section>
                    <section id='task' className='space-y-4'>
                        <HcTaskManagement />
                    </section>
                </TabsContent>

                <TabsContent value='faq' className='space-y-4'>
                    <div className='space-y-2'>
                        <h2 className='text-2xl font-semibold'>常见问题（FAQ）</h2>
                        <p className='text-muted-foreground'>支持按关键字搜索问题与答案。</p>
                    </div>
                    <SearchBox value={query} onChange={setQuery} />
                    <FaqList query={query} />
                </TabsContent>

                <TabsContent value='contact' className='space-y-4'>
                    <HcContact />
                </TabsContent>
            </Tabs>
        </div>
    )
}

export default HelpCenter

