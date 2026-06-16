import React, { useCallback, useEffect, useRef, useState } from 'react'

const AMAP_KEY = '1e1313769f138588c0dd985e6892cc27'
// 默认中心设为同济大学嘉定校区 (lng, lat)
// 使用提供的精确坐标：经度 121.215252，纬度 31.286054
const defaultCenter: [number, number] = [121.215252, 31.286054]

type MapPickerProps = {
  initial?: { latitude: number; longitude: number }
  height?: number | string
  onSelect?: (lat: number, lng: number) => void
}

export default function MapPicker({ initial, height = 400, onSelect }: MapPickerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<any | null>(null)
  const markerRef = useRef<any | null>(null)
  const isLoaded = useRef(false)

  const initMap = useCallback(() => {
    if (!containerRef.current || mapRef.current) return
    const AMap = (window as any).AMap
    if (!AMap) return
    const center = initial ? [initial.longitude, initial.latitude] : defaultCenter
    const map = new AMap.Map(containerRef.current, {
      viewMode: '2D',
      zoom: 15,
      center,
    })
    mapRef.current = map
    // ensure correct view after container becomes visible
    setTimeout(() => {
      try {
        map.setCenter(center)
        map.setZoom(15)
        if (typeof map.setFitView === 'function') map.setFitView()
      } catch (e) {
        // ignore
      }
    }, 150)

    map.on('click', (e: any) => {
      const lng = e.lnglat.lng
      const lat = e.lnglat.lat
      if (!markerRef.current) {
        markerRef.current = new AMap.Marker({
          position: [lng, lat],
          map,
        })
      } else {
        markerRef.current.setPosition([lng, lat])
      }
      // center map on selected point to improve UX
      try {
        map.setCenter([lng, lat])
      } catch (err) {}
      onSelect?.(lat, lng)
    })

    // place initial marker if provided
    if (initial) {
      markerRef.current = new AMap.Marker({
        position: [initial.longitude, initial.latitude],
        map,
      })
      setTimeout(() => {
        try {
          map.setCenter([initial.longitude, initial.latitude])
          if (typeof map.setFitView === 'function') map.setFitView()
        } catch (e) {}
      }, 100)
    }
  }, [initial, onSelect])

  useEffect(() => {
    if (typeof window.AMap !== 'undefined' || isLoaded.current) {
      if (containerRef.current && !mapRef.current) initMap()
      return
    }

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_KEY}`
    script.async = true
    script.onload = () => {
      isLoaded.current = true
      initMap()
    }
    document.body.appendChild(script)
    return () => {
      if (mapRef.current) {
        mapRef.current.destroy()
        mapRef.current = null
      }
    }
  }, [initMap])

  const heightValue = typeof height === 'number' ? `${height}px` : height
  return <div ref={containerRef} style={{ height: heightValue, width: '100%' }} className='rounded-lg border' />
}

declare global {
  interface Window {
    AMap: any
  }
}
