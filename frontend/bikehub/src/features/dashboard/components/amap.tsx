import React, { useEffect, useRef, useState } from 'react'
import { Station } from '@/features/station_management/data/schema'

const AMAP_KEY = '1e1313769f138588c0dd985e6892cc27'
const AMAP_SECURITY_KEY = '3a617c0365076abeea276731d5453887'

window._AMapSecurityConfig = {
    securityJsCode: AMAP_SECURITY_KEY,
}

const defaultCenter: [number, number] = [121.215252, 31.286054]

export type AmapMode = 'heatmap' | 'markers'

type AmapComponentProps = {
    mode?: AmapMode
    height?: number | string
    data?: Station[]
}

export function AmapComponent({ mode = 'markers', height = 400, data = [] }: AmapComponentProps) {
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
            // Only remove script if it's the last map? 
            // Actually, removing the script tag might break other maps if they are loading.
            // But usually we don't remove the script tag in SPA.
            // The original code removed it. I'll keep it but be careful.
            // document.body.removeChild(script) 

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

        // Clear existing visualizations
        if (heatmapRef.current) {
            heatmapRef.current.setDataSet({ data: [], max: 0 })
            heatmapRef.current.hide()
        }
        if (markersRef.current.length > 0) {
            map.remove(markersRef.current)
            markersRef.current = []
        }

        if (mode === 'heatmap') {
            AMap.plugin(['AMap.HeatMap'], function () {
                if (!heatmapRef.current) {
                    heatmapRef.current = new AMap.HeatMap(map, {
                        radius: 25,
                        opacity: [0, 0.8],
                    })
                }
                heatmapRef.current.show()

                const points = data.map((station) => ({
                    lng: station.longitude,
                    lat: station.latitude,
                    count: station.capacity,
                }))

                const max = Math.max(...points.map((p) => p.count), 10)

                heatmapRef.current.setDataSet({
                    data: points,
                    max: max,
                })
            })
        } else if (mode === 'markers') {
            data.forEach((station) => {
                const marker = new AMap.Marker({
                    position: [station.longitude, station.latitude],
                    title: station.name,
                    map: map,
                })
                markersRef.current.push(marker)
            })
            map.setFitView()
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
