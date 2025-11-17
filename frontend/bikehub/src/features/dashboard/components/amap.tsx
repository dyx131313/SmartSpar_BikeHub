import React, { useEffect, useRef } from 'react'

// 替换为你的高德 Key 和安全密钥
const AMAP_KEY = '1e1313769f138588c0dd985e6892cc27'
const AMAP_SECURITY_KEY = '3a617c0365076abeea276731d5453887'

// 设置安全密钥，防止加载失败
// @ts-ignore
window._AMapSecurityConfig = {
    securityJsCode: AMAP_SECURITY_KEY,
}

const defaultCenter: [number, number] = [121.215252, 31.286054] // 默认中心点：同济大学嘉定校区

export function AmapComponent() {
    const mapContainerRef = useRef<HTMLDivElement>(null)
    const isMapLoaded = useRef(false)

    useEffect(() => {
        // 检查 AMap 对象是否存在，以避免重复加载脚本
        if (typeof window.AMap !== 'undefined' || isMapLoaded.current) {
            if (mapContainerRef.current) {
                initMap()
            }
            return
        }

        // 1. 动态创建 script 标签加载高德地图 API
        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
        script.async = true

        script.onload = () => {
            isMapLoaded.current = true
            initMap()
        }

        // 2. 将 script 标签插入到 body
        document.body.appendChild(script)

        // 3. 组件卸载时清理 script 和 map 实例
        return () => {
            document.body.removeChild(script)
            // 清理地图实例（如果需要）
            if (window.AMap && window.mapInstance) {
                window.mapInstance.destroy()
            }
        }
    }, []) // 仅在组件挂载和卸载时执行

    const initMap = () => {
        if (mapContainerRef.current) {
            // @ts-ignore
            const AMap = window.AMap

            if (AMap) {
                // 创建地图实例
                // @ts-ignore
                window.mapInstance = new AMap.Map(mapContainerRef.current, {
                    viewMode: '2D', // 使用 2D 模式
                    zoom: 11, // 初始缩放级别
                    center: defaultCenter, // 初始中心点
                })

                // 可选：添加地图控件
                AMap.plugin(['AMap.ToolBar', 'AMap.Scale'], function () {
                    // @ts-ignore
                    window.mapInstance.addControl(new AMap.ToolBar())
                    // @ts-ignore
                    window.mapInstance.addControl(new AMap.Scale())
                })
            }
        }
    }

    // 需要一个固定的高度才能显示地图
    return (
        <div
            ref={mapContainerRef}
            style={{ height: '400px', width: '100%' }} // 确保容器有高度和宽度
            className="rounded-lg border"
        />
    )
}

// 扩展 Window 接口以避免 TypeScript 错误（可选，但推荐）
declare global {
    interface Window {
        AMap: any;
        mapInstance: any;
        _AMapSecurityConfig: {
            securityJsCode: string;
        };
    }
}