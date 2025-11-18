import React, { useEffect, useRef } from 'react'

// �滻Ϊ��ĸߵ� Key �Ͱ�ȫ��Կ
const AMAP_KEY = '1e1313769f138588c0dd985e6892cc27'
const AMAP_SECURITY_KEY = '3a617c0365076abeea276731d5453887'

// ���ð�ȫ��Կ����ֹ����ʧ��
// @ts-ignore
window._AMapSecurityConfig = {
    securityJsCode: AMAP_SECURITY_KEY,
}

const defaultCenter: [number, number] = [121.215252, 31.286054] // Ĭ�����ĵ㣺ͬ�ô�ѧ�ζ�У��

export type AmapMode = 'heatmap' | 'markers'

type AmapComponentProps = {
    mode?: AmapMode
    height?: number | string
}

export function AmapComponent({ mode = 'markers', height = 400 }: AmapComponentProps) {
    const mapContainerRef = useRef<HTMLDivElement>(null)
    const isMapLoaded = useRef(false)

    useEffect(() => {
        // ��� AMap �����Ƿ���ڣ��Ա����ظ����ؽű�
        if (typeof window.AMap !== 'undefined' || isMapLoaded.current) {
            if (mapContainerRef.current) {
                initMap()
            }
            return
        }

        // 1. ��̬���� script ��ǩ���ظߵµ�ͼ API
        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
        script.async = true

        script.onload = () => {
            isMapLoaded.current = true
            initMap()
        }

        // 2. �� script ��ǩ���뵽 body
        document.body.appendChild(script)

        // 3. ���ж��ʱ���� script �� map ʵ��
        return () => {
            document.body.removeChild(script)
            // ������ͼʵ���������Ҫ��
            if (window.AMap && window.mapInstance) {
                window.mapInstance.destroy()
            }
        }
    }, []) // ����������غ�ж��ʱִ��

    const initMap = () => {
        if (mapContainerRef.current) {
            // @ts-ignore
            const AMap = window.AMap

            if (AMap) {
                // ������ͼʵ��
                // @ts-ignore
                window.mapInstance = new AMap.Map(mapContainerRef.current, {
                    viewMode: '2D', // ʹ�� 2D ģʽ
                    zoom: 11, // ��ʼ���ż���
                    center: defaultCenter, // ��ʼ���ĵ�
                })

                // ��ѡ�����ӵ�ͼ�ؼ�
                AMap.plugin(['AMap.ToolBar', 'AMap.Scale'], function () {
                    // @ts-ignore
                    window.mapInstance.addControl(new AMap.ToolBar())
                    // @ts-ignore
                    window.mapInstance.addControl(new AMap.Scale())
                })

                // TODO: 依据 mode 渲染热力图或点标注（接入现有 API 数据）
                // if (mode === 'heatmap') { /* 添加热力图图层 */ } else { /* 添加点标注/聚合 */ }
            }
        }
    }

    // ��Ҫһ���̶��ĸ߶Ȳ�����ʾ��ͼ
    const heightValue = typeof height === 'number' ? `${height}px` : height
    return (
        <div
            ref={mapContainerRef}
            style={{ height: heightValue, width: '100%' }} // ȷ�������и߶ȺͿ���
            className="rounded-lg border"
        />
    )
}

// ��չ Window �ӿ��Ա��� TypeScript ���󣨿�ѡ�����Ƽ���
declare global {
    interface Window {
        AMap: any;
        mapInstance: any;
        _AMapSecurityConfig: {
            securityJsCode: string;
        };
    }
}