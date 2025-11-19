import React, { useEffect, useRef } from 'react'

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
}

export function AmapComponent({ mode = 'markers', height = 400 }: AmapComponentProps) {
    const mapContainerRef = useRef<HTMLDivElement>(null)
    const isMapLoaded = useRef(false)

    useEffect(() => {
        if (typeof window.AMap !== 'undefined' || isMapLoaded.current) {
            if (mapContainerRef.current) {
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
            document.body.removeChild(script)
            if (window.AMap && window.mapInstance) {
                window.mapInstance.destroy()
            }
        }
    }, [])

    const initMap = () => {
        if (mapContainerRef.current) {
            const AMap = window.AMap

            if (AMap) {
                window.mapInstance = new AMap.Map(mapContainerRef.current, {
                    viewMode: '2D',
                    zoom: 11,
                    center: defaultCenter,
                })

                AMap.plugin(['AMap.ToolBar', 'AMap.Scale'], function () {
                    window.mapInstance.addControl(new AMap.ToolBar())
                    window.mapInstance.addControl(new AMap.Scale())
                })
            }
        }
    }

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