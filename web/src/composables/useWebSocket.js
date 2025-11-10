import { ref, computed, watch, onUnmounted } from 'vue'
import { useMessage } from 'naive-ui'

/**
 * WebSocket 连接组合式函数
 * @param {string} url WebSocket连接地址
 * @param {Object} options 配置选项
 * @returns {Object} WebSocket相关状态和方法
 */
export function useWebSocket(url, options = {}) {
  const {
    autoConnect = true,
    reconnectLimit = 5,
    reconnectInterval = 3000,
    heartbeatInterval = 30000,
    onMessage = () => {},
    onError = () => {},
    onOpen = () => {},
    onClose = () => {},
  } = options

  const message = useMessage()

  // 状态管理
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const reconnectCount = ref(0)
  const lastMessage = ref(null)
  const error = ref(null)

  let ws = null
  let reconnectTimer = null
  let heartbeatTimer = null

  /**
   * 建立WebSocket连接
   * @param {string} newUrl 可选的新连接地址
   */
  const connect = (newUrl) => {
    if (isConnecting.value || isConnected.value) {
      // 如果已经连接，但URL发生变化，则先断开
      if (newUrl && ws && ws.url !== newUrl) {
        disconnect()
      } else {
        return
      }
    }

    isConnecting.value = true
    error.value = null

    // 决定使用哪个URL
    const targetUrl = newUrl || ws?.url || url

    try {
      ws = new WebSocket(targetUrl)

      ws.onopen = (event) => {
        isConnected.value = true
        isConnecting.value = false
        reconnectCount.value = 0
        error.value = null

        // 启动心跳
        startHeartbeat()

        onOpen(event)
        console.log('WebSocket连接已建立')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          lastMessage.value = data
          onMessage(data)
        } catch (err) {
          console.error('解析WebSocket消息失败:', err)
          lastMessage.value = event.data
          onMessage(event.data)
        }
      }

      ws.onclose = (event) => {
        isConnected.value = false
        isConnecting.value = false

        // 停止心跳
        stopHeartbeat()

        onClose(event)

        // 如果不是主动关闭，尝试重连
        if (event.code !== 1000 && reconnectCount.value < reconnectLimit) {
          scheduleReconnect()
        } else if (reconnectCount.value >= reconnectLimit) {
          error.value = '连接失败，已达到最大重连次数'
          message.error('WebSocket连接失败，请检查网络连接')
        }

        console.log('WebSocket连接已关闭', event.code, event.reason)
      }

      ws.onerror = (event) => {
        error.value = 'WebSocket连接错误'
        isConnecting.value = false
        onError(event)
        console.error('WebSocket连接错误:', event)
      }
    } catch (err) {
      isConnecting.value = false
      error.value = err.message
      console.error('创建WebSocket连接失败:', err)
    }
  }

  /**
   * 关闭WebSocket连接
   */
  const disconnect = () => {
    if (ws) {
      ws.close(1000, '主动关闭连接')
    }

    // 清理定时器
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    stopHeartbeat()

    isConnected.value = false
    isConnecting.value = false
    reconnectCount.value = 0
  }

  /**
   * 发送消息
   * @param {*} data 要发送的数据
   */
  const send = (data) => {
    if (!isConnected.value || !ws) {
      console.warn('WebSocket未连接，无法发送消息')
      return false
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data)
      ws.send(message)
      return true
    } catch (err) {
      console.error('发送WebSocket消息失败:', err)
      return false
    }
  }

  /**
   * 安排重连
   */
  const scheduleReconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
    }

    reconnectCount.value++
    console.log(`准备第${reconnectCount.value}次重连...`)

    reconnectTimer = setTimeout(() => {
      connect()
    }, reconnectInterval)
  }

  /**
   * 启动心跳
   */
  const startHeartbeat = () => {
    if (heartbeatInterval <= 0) return

    heartbeatTimer = setInterval(() => {
      if (isConnected.value) {
        send({ type: 'ping', timestamp: Date.now() })
      }
    }, heartbeatInterval)
  }

  /**
   * 停止心跳
   */
  const stopHeartbeat = () => {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  /**
   * 手动重连
   */
  const reconnect = () => {
    disconnect()
    setTimeout(() => {
      reconnectCount.value = 0
      connect()
    }, 1000)
  }

  // 自动连接
  if (autoConnect) {
    connect()
  }

  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    // 状态
    isConnected,
    isConnecting,
    reconnectCount,
    lastMessage,
    error,

    // 方法
    connect,
    disconnect,
    send,
    reconnect,
  }
}

/**
 * 设备实时数据WebSocket连接
 * @param {Object} options 配置选项
 * @returns {Object} 设备数据相关状态和方法
 */
export function useDeviceWebSocket(options = {}) {
  const {
    deviceType = '',
    deviceCodes = null, // 新增：设备编码列表
    onDataUpdate = () => {},
    ...wsOptions
  } = options

  // 获取认证token
  const getToken = () => {
    return localStorage.getItem('access_token')
  }

  // 构建WebSocket URL的函数
  const buildWebSocketUrl = () => {
    // WebSocket端点在v2 API中，需要使用正确的路径
    const baseApi = '/api/v2' // WebSocket端点在v2版本中
    // 构建完整的WebSocket URL - 连接到后端端口8001
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.hostname + ':8001' // 明确指定后端端口8001
    let wsUrl = `${wsProtocol}//${wsHost}${baseApi}/devices/realtime-data/ws`

    // 添加查询参数
    const params = new URLSearchParams()

    // 添加token认证
    const token = getToken()
    if (token) {
      params.append('token', token)
    }

    if (deviceType) {
      params.append('type_code', deviceType)
    }

    // 移除 device_codes 参数，以避免后端问题并保持单一稳定连接
    // const currentDeviceCodes = computed(() => deviceCodes?.value || deviceCodes)
    // const codes = currentDeviceCodes.value
    // if (codes && Array.isArray(codes) && codes.length > 0) {
    //   params.append('device_codes', codes.join(','))
    // }

    // 使用固定的page_size值，与后端默认值保持一致
    params.append('page_size', '100') // 固定page_size，足够处理大部分场景

    if (params.toString()) {
      wsUrl += '?' + params.toString()
    }

    console.log('WebSocket连接URL:', wsUrl)
    console.log('使用token:', token ? '已设置' : '未设置')
    // console.log('设备编码列表:', codes) // codes is not defined after refactoring

    return wsUrl
  }

  const deviceData = ref([])
  const deviceSummary = ref({})

  // 初始URL
  const initialUrl = buildWebSocketUrl()

  const { isConnected, isConnecting, error, connect, disconnect, send, reconnect } = useWebSocket(
    initialUrl,
    {
      ...wsOptions,
      onMessage: (data) => {
        handleDeviceMessage(data)
        wsOptions.onMessage?.(data)
      },
      onOpen: (event) => {
        console.log('WebSocket连接已建立，设备类型:', deviceType || '全部')
        wsOptions.onOpen?.(event)
      },
    }
  )

  // 防抖定时器
  let reconnectTimer = null

  // 移除对 deviceCodes 的监听，我们现在保持一个单一的、稳定的连接

  /**
   * 处理设备数据消息
   */
  const handleDeviceMessage = (data) => {
    try {
      if (data.type === 'realtime_data') {
        // 更新设备实时数据
        const items = data.data?.data || data.data?.items || data.data || []
        deviceData.value = items
        onDataUpdate(items)
      } else if (data.type === 'device_summary') {
        // 更新设备状态汇总
        deviceSummary.value = data.data || {}
      } else if (data.type === 'device_update') {
        // 单个设备数据更新
        const updatedDevice = data.data
        if (updatedDevice) {
          const index = deviceData.value.findIndex(
            (d) => d.device_code === updatedDevice.device_code
          )
          if (index >= 0) {
            deviceData.value[index] = updatedDevice
          } else {
            deviceData.value.push(updatedDevice)
          }
          onDataUpdate(deviceData.value)
        }
      } else if (data.type === 'error') {
        // 处理错误消息
        console.error('WebSocket错误:', data.message)
      } else if (data.type === 'ping') {
        // 心跳消息，无需处理
        console.log('收到心跳消息')
      }
    } catch (err) {
      console.error('处理设备WebSocket消息失败:', err)
    }
  }

  /**
   * 订阅设备类型数据
   */
  const subscribeDeviceType = (typeCode) => {
    send({
      type: 'subscribe',
      device_type: typeCode,
      timestamp: Date.now(),
    })
  }

  /**
   * 取消订阅设备类型数据
   */
  const unsubscribeDeviceType = (typeCode) => {
    send({
      type: 'unsubscribe',
      device_type: typeCode,
      timestamp: Date.now(),
    })
  }

  /**
   * 请求设备数据刷新
   */
  const requestRefresh = (typeCode = '') => {
    send({
      type: 'refresh',
      device_type: typeCode,
      timestamp: Date.now(),
    })
  }

  return {
    // 状态
    isConnected,
    isConnecting,
    error,
    deviceData,
    deviceSummary,

    // 方法
    connect,
    disconnect,
    reconnect,
    subscribeDeviceType,
    unsubscribeDeviceType,
    requestRefresh,
  }
}
