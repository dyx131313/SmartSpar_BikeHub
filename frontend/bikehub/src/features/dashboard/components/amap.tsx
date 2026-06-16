import React, { useCallback, useEffect, useRef, useState } from 'react'
import { type StationDashboardData } from '@/features/station_management/data/schema'

const AMAP_KEY = '1e1313769f138588c0dd985e6892cc27'
const AMAP_SECURITY_KEY = '3a617c0365076abeea276731d5453887'

window._AMapSecurityConfig = {
    securityJsCode: AMAP_SECURITY_KEY,
}

// 默认中心设为同济大学嘉定校区 (lng, lat)
// 使用提供的精确坐标：经度 121.215252，纬度 31.286054
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
    const baseMapReadyRef = useRef(false)
    const [mapReady, setMapReady] = useState(false)
    const [baseMapReady, setBaseMapReady] = useState(false)
    const [useFallbackMap, setUseFallbackMap] = useState(false)

    const initMap = useCallback(() => {
        if (mapContainerRef.current && !mapInstanceRef.current) {
            const AMap = window.AMap

            if (AMap) {
                const map = new AMap.Map(mapContainerRef.current, {
                    viewMode: '2D',
                    zoom: 11,
                    center: defaultCenter,
                })
                map.on('complete', () => {
                    baseMapReadyRef.current = true
                    setBaseMapReady(true)
                    setUseFallbackMap(false)
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
    }, [])

    useEffect(() => {
        const fallbackTimer = window.setTimeout(() => {
            if (!baseMapReadyRef.current) {
                setUseFallbackMap(true)
            }
        }, 4500)

        if (typeof window.AMap !== 'undefined' || isMapLoaded.current) {
            if (mapContainerRef.current && !mapInstanceRef.current) {
                initMap()
            }
            return () => window.clearTimeout(fallbackTimer)
        }

        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
        script.async = true

        script.onload = () => {
            isMapLoaded.current = true
            initMap()
        }
        script.onerror = () => {
            setUseFallbackMap(true)
        }

        document.body.appendChild(script)

        return () => {
            window.clearTimeout(fallbackTimer)
            if (mapInstanceRef.current) {
                mapInstanceRef.current.destroy()
                mapInstanceRef.current = null
            }
        }
    }, [initMap])

    useEffect(() => {
        if (!mapReady || !mapInstanceRef.current || !window.AMap) return

        const map = mapInstanceRef.current
        const AMap = window.AMap

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
                } else {
                    // 预测需求热力图 (默认)
                    points = data.map((station) => ({
                        lng: station.longitude,
                        lat: station.latitude,
                        count: station.predicted_demand || 0,
                    }))
                }

                const max = Math.max(...points.map((p) => p.count), 10)

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
                    // 2秒后隐藏，除非期间再次触发 showLabel
                    hideTimer = setTimeout(() => {
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
            style={{ height: heightValue, width: '100%' }}
            className="border-border/70 relative min-h-[360px] overflow-hidden rounded-md border bg-muted shadow-sm"
        >
            <div
                ref={mapContainerRef}
                className={useFallbackMap ? 'hidden' : 'h-full w-full'}
            />
            {useFallbackMap && <FallbackCampusMap data={data} />}
            {!useFallbackMap && !baseMapReady && (
                <div className="pointer-events-none absolute inset-x-4 bottom-4 rounded-md border border-border/70 bg-background/90 px-3 py-2 text-xs text-muted-foreground shadow-sm">
                    正在加载高德地图，若 Key 或网络不可用将自动切换为本地站点图。
                </div>
            )}
        </div>
    )
}

function FallbackCampusMap({ data }: { data: StationDashboardData[] }) {
    if (data.length === 0) {
        return (
            <div className="flex h-full items-center justify-center bg-muted text-sm text-muted-foreground">
                暂无站点坐标数据
            </div>
        )
    }

    const longitudes = data.map((station) => Number(station.longitude))
    const latitudes = data.map((station) => Number(station.latitude))
    const minLng = Math.min(...longitudes)
    const maxLng = Math.max(...longitudes)
    const minLat = Math.min(...latitudes)
    const maxLat = Math.max(...latitudes)
    const lngSpan = Math.max(maxLng - minLng, 0.001)
    const latSpan = Math.max(maxLat - minLat, 0.001)

    const project = (station: StationDashboardData) => {
        const x = 8 + ((Number(station.longitude) - minLng) / lngSpan) * 84
        const y = 10 + ((maxLat - Number(station.latitude)) / latSpan) * 78
        return { left: `${x}%`, top: `${y}%` }
    }

    return (
        <div className="relative h-full w-full overflow-hidden bg-[linear-gradient(0deg,rgba(148,163,184,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.12)_1px,transparent_1px)] bg-[size:28px_28px] bg-slate-950">
            <div className="absolute left-4 top-4 rounded-md border border-white/10 bg-slate-900/85 px-3 py-2 text-xs text-slate-300 shadow-sm">
                高德底图不可用，已切换本地站点分布图
            </div>
            <div className="absolute inset-x-8 top-1/2 h-px bg-cyan-300/20" />
            <div className="absolute bottom-8 left-1/2 top-8 w-px bg-cyan-300/20" />
            {data.map((station) => {
                const position = project(station)
                const bikes = station.current_bikes || 0
                const demand = station.real_demand || station.predicted_demand || 0
                const pressure = demand > bikes ? 'border-rose-300 bg-rose-500' : 'border-emerald-300 bg-emerald-500'

                return (
                    <div
                        key={station.id}
                        className="absolute -translate-x-1/2 -translate-y-1/2"
                        style={position}
                    >
                        <div className={`h-4 w-4 rounded-full border-2 shadow-lg shadow-black/30 ${pressure}`} />
                        <div className="mt-1 min-w-28 rounded-md border border-white/10 bg-slate-900/90 px-2 py-1 text-xs text-white shadow-sm">
                            <div className="truncate font-medium">{station.name}</div>
                            <div className="text-slate-300">车 {bikes} / 需 {demand}</div>
                        </div>
                    </div>
                )
            })}
        </div>
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
