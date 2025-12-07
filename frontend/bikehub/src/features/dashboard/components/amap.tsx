import React, { useEffect, useRef, useState } from 'react'
import { StationDashboardData } from '@/features/station_management/data/schema'

const AMAP_KEY = '1e1313769f138588c0dd985e6892cc27'
const AMAP_SECURITY_KEY = '3a617c0365076abeea276731d5453887'

window._AMapSecurityConfig = {
    securityJsCode: AMAP_SECURITY_KEY,
}

const defaultCenter: [number, number] = [121.215252, 31.286054]

export type AmapMode = 'heatmap' | 'markers' | 'combined' | 'real_demand_heatmap'

type AmapComponentProps = {
    mode?: AmapMode
    height?: number | string
    data?: StationDashboardData[]
}

export function AmapComponent({ mode = 'combined', height = 400, data = [] }: AmapComponentProps) {
    const mapContainerRef = useRef<HTMLDivElement>(null)
    const mapInstanceRef = useRef<any>(null)
    const heatmapRef = useRef<any>(null)
    const markersRef = useRef<any[]>([])
    const isMapLoaded = useRef(false)
    const [mapReady, setMapReady] = useState(false)

    useEffect(() => {
        if (typeof window.AMap !== 'undefined' || isMapLoaded.current) {
            if (mapContainerRef.current && !mapInstanceRef.current) {
                initMap()
            }
            return
        }

        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
        script.async = true

        script.onload = () => {
            isMapLoaded.current = true
            initMap()
        }

        document.body.appendChild(script)

        return () => {
            if (mapInstanceRef.current) {
                mapInstanceRef.current.destroy()
                mapInstanceRef.current = null
            }
        }
    }, [])

    const initMap = () => {
        if (mapContainerRef.current && !mapInstanceRef.current) {
            const AMap = window.AMap

            if (AMap) {
                const map = new AMap.Map(mapContainerRef.current, {
                    viewMode: '2D',
                    zoom: 11,
                    center: defaultCenter,
                })

                mapInstanceRef.current = map
                window.mapInstance = map

                AMap.plugin(['AMap.ToolBar', 'AMap.Scale'], function () {
                    map.addControl(new AMap.ToolBar())
                    map.addControl(new AMap.Scale())
                })

                setMapReady(true)
            }
        }
    }

    useEffect(() => {
        if (!mapReady || !mapInstanceRef.current || !window.AMap) return

        const map = mapInstanceRef.current
        const AMap = window.AMap

        console.log('AmapComponent update:', { mode, dataLength: data.length, dataSample: data[0] })

        // Clear existing visualizations
        if (heatmapRef.current) {
            heatmapRef.current.setDataSet({ data: [], max: 0 })
            heatmapRef.current.hide()
        }
        if (markersRef.current.length > 0) {
            map.remove(markersRef.current)
            markersRef.current = []
        }

        const showHeatmap = mode === 'heatmap' || mode === 'combined' || mode === 'real_demand_heatmap'
        const showMarkers = mode === 'markers' || mode === 'combined'

        if (showHeatmap) {
            AMap.plugin(['AMap.HeatMap'], function () {
                if (!heatmapRef.current) {
                    heatmapRef.current = new AMap.HeatMap(map, {
                        radius: 25,
                        opacity: [0, 0.8],
                    })
                }
                heatmapRef.current.show()

                // 根据模式选择热力图数据源
                let points: any[] = []
                if (mode === 'real_demand_heatmap') {
                    // 真实需求热力图
                    points = data.map((station) => ({
                        lng: station.longitude,
                        lat: station.latitude,
                        count: station.real_demand || 0,
                    }))
                    console.log('Real demand points:', points.slice(0, 5))
                } else {
                    // 预测需求热力图 (默认)
                    points = data.map((station) => ({
                        lng: station.longitude,
                        lat: station.latitude,
                        count: station.predicted_demand || 0,
                    }))
                    console.log('Predicted demand points:', points.slice(0, 5))
                }

                const max = Math.max(...points.map((p) => p.count), 10)
                console.log('Heatmap max:', max)

                heatmapRef.current.setDataSet({
                    data: points,
                    max: max,
                })
            })
        }

        if (showMarkers) {
            data.forEach((station) => {
                // 使用默认图标，初始不显示详细信息，避免遮挡和重叠
                const marker = new AMap.Marker({
                    position: [station.longitude, station.latitude],
                    title: station.name, // 鼠标悬停时的原生提示
                    map: map,
                    anchor: 'bottom-center', // 图标底部中心对准坐标
                })

                // 横向展示的详情框内容
                const labelContent = `
                    <div style="
                        display: flex;
                        flex-direction: row;
                        align-items: center;
                        padding: 6px 10px;
                        background: white;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                        font-size: 12px;
                        white-space: nowrap;
                        color: #333;
                        pointer-events: none;
                    ">
                        <div style="font-weight: bold; margin-right: 8px; color: #000;">${station.name}</div>
                        <div style="color: #666;">🚲 ${station.current_bikes || 0} / ${station.capacity}</div>
                    </div>
                `

                // 鼠标悬浮或点击时显示详情
                let hideTimer: any = null

                const showLabel = () => {
                    console.log('Show label:', station.name)
                    if (hideTimer) {
                        clearTimeout(hideTimer)
                        hideTimer = null
                    }
                    marker.setLabel({
                        content: labelContent,
                        direction: 'top',
                        offset: new AMap.Pixel(0, -5)
                    })
                    marker.setTop(true) // 置顶显示
                }

                const hideLabel = () => {
                    console.log('Mouse out, schedule hide:', station.name)
                    // 2秒后隐藏，除非期间再次触发 showLabel
                    hideTimer = setTimeout(() => {
                        console.log('Hiding label now:', station.name)
                        marker.setLabel({ content: '' }) // 使用空内容来隐藏
                        marker.setTop(false)
                    }, 2000)
                }

                marker.on('mouseover', showLabel)
                marker.on('mouseout', hideLabel)
                // 点击也能触发
                marker.on('click', showLabel)

                markersRef.current.push(marker)
            })
            // Only fit view if we have markers, otherwise map might zoom to 0,0
            if (data.length > 0) {
                map.setFitView()
            }
        }
    }, [mapReady, mode, data])

    const heightValue = typeof height === 'number' ? `${height}px` : height
    return (
        <div
            ref={mapContainerRef}
            style={{ height: heightValue, width: '100%' }}
            className="rounded-lg border"
        />
    )
}

declare global {
    interface Window {
        AMap: any;
        mapInstance: any;
        _AMapSecurityConfig: {
            securityJsCode: string;
        };
    }
}
