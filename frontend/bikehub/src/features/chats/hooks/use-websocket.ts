/**
 * WebSocket Hook
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { getAuthToken } from '@/lib/auth';
import { ChatNotificationMessage, WebSocketMessage } from '../data/group-chat-types';

interface UseWebSocketOptions {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onNewMessage?: (message: ChatNotificationMessage) => void;
  onUserTyping?: (data: { group_id: number; user_id: number; is_typing: boolean }) => void;
  onUserStatusChanged?: (data: { user_id: number; status: 'online' | 'offline' }) => void;
  onMemberJoined?: (data: { group_id: number; member: any }) => void;
  onMemberLeft?: (data: { group_id: number; user_id: number }) => void;
  onGroupUpdated?: (data: any) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  pingInterval?: number;
}

interface WebSocketState {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  reconnectCount: number;
  lastPing?: Date;
  groups: number[];
  onlineCount: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    onNewMessage,
    onUserTyping,
    onUserStatusChanged,
    onMemberJoined,
    onMemberLeft,
    onGroupUpdated,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    pingInterval = 30000,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    connected: false,
    connecting: false,
    error: null,
    reconnectCount: 0,
    groups: [],
    onlineCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const pingIntervalRef = useRef<NodeJS.Timeout>();
  const messageQueueRef = useRef<any[]>([]);

  // WebSocket服务器地址
  const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8765'}?token=${getAuthToken()}`;

  // 连接WebSocket
  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    setState(prev => ({ ...prev, connecting: true, error: null }));

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setState(prev => ({
          ...prev,
          connected: true,
          connecting: false,
          error: null,
          reconnectCount: 0,
        }));

        // 发送消息队列中的消息
        while (messageQueueRef.current.length > 0) {
          const message = messageQueueRef.current.shift();
          ws.send(JSON.stringify(message));
        }

        // 设置ping间隔
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, pingInterval);

        onConnect?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          setState(prev => ({
            ...prev,
            lastPing: new Date(),
          }));

          // 处理不同类型的消息
          switch (message.type) {
            case 'connection_success':
              setState(prev => ({
                ...prev,
                groups: message.data.groups || [],
                onlineCount: message.data.online_count || 0,
              }));
              break;

            case 'unread_count':
              // 可以更新未读消息数量
              break;

            case 'new_message':
              onNewMessage?.(message as ChatNotificationMessage);
              break;

            case 'user_typing':
              onUserTyping?.(message.data);
              break;

            case 'user_status_changed':
              onUserStatusChanged?.(message.data);
              break;

            case 'member_joined':
              onMemberJoined?.(message.data);
              break;

            case 'member_left':
              onMemberLeft?.(message.data);
              break;

            case 'group_updated':
              onGroupUpdated?.(message.data);
              break;

            case 'pong':
              // 收到pong响应，保持连接
              break;

            default:
              onMessage?.(message);
          }

        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      ws.onclose = (event) => {
        setState(prev => ({
          ...prev,
          connected: false,
          connecting: false,
        }));

        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        onDisconnect?.();

        // 自动重连
        if (!event.wasClean && state.reconnectCount < reconnectAttempts) {
          setState(prev => ({
            ...prev,
            reconnectCount: prev.reconnectCount + 1,
          }));

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval * Math.pow(2, state.reconnectCount)); // 指数退避
        }
      };

      ws.onerror = (error) => {
        setState(prev => ({
          ...prev,
          connected: false,
          connecting: false,
          error: 'WebSocket连接错误',
        }));

        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        onError?.(error);
      };

    } catch (error) {
      setState(prev => ({
        ...prev,
        connected: false,
        connecting: false,
        error: '无法创建WebSocket连接',
      }));

      console.error('WebSocket连接失败:', error);
    }
  }, [
    wsUrl,
    state.reconnectCount,
    reconnectAttempts,
    reconnectInterval,
    pingInterval,
    onConnect,
    onDisconnect,
    onError,
    onMessage,
    onNewMessage,
    onUserTyping,
    onUserStatusChanged,
    onMemberJoined,
    onMemberLeft,
    onGroupUpdated,
  ]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setState(prev => ({
      ...prev,
      connected: false,
      connecting: false,
      error: null,
      reconnectCount: 0,
    }));
  }, []);

  // 发送消息
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      // 连接未建立时，将消息加入队列
      messageQueueRef.current.push(message);

      // 尝试重新连接
      if (!state.connecting && state.reconnectCount === 0) {
        connect();
      }
    }
  }, [state.connecting, state.reconnectCount, connect]);

  // 加入群聊
  const joinGroup = useCallback((groupId: number) => {
    sendMessage({
      type: 'join_group',
      group_id: groupId,
    });

    setState(prev => ({
      ...prev,
      groups: [...prev.groups, groupId],
    }));
  }, [sendMessage]);

  // 离开群聊
  const leaveGroup = useCallback((groupId: number) => {
    sendMessage({
      type: 'leave_group',
      group_id: groupId,
    });

    setState(prev => ({
      ...prev,
      groups: prev.groups.filter(id => id !== groupId),
    }));
  }, [sendMessage]);

  // 标记消息为已读
  const markAsRead = useCallback((messageId: number) => {
    sendMessage({
      type: 'mark_as_read',
      message_id: messageId,
    });
  }, [sendMessage]);

  // 发送正在输入状态
  const sendTyping = useCallback((groupId: number, isTyping: boolean) => {
    sendMessage({
      type: 'typing',
      group_id: groupId,
      is_typing: isTyping,
    });
  }, [sendMessage]);

  // 初始化连接
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, []);

  return {
    // 状态
    connected: state.connected,
    connecting: state.connecting,
    error: state.error,
    reconnectCount: state.reconnectCount,
    lastPing: state.lastPing,
    groups: state.groups,
    onlineCount: state.onlineCount,

    // 方法
    connect,
    disconnect,
    sendMessage,
    joinGroup,
    leaveGroup,
    markAsRead,
    sendTyping,
  };
};

// WebSocket Hook for chat functionality
export const useChatWebSocket = (currentGroupId?: number) => {
  const [typingUsers, setTypingUsers] = useState<Set<number>>(new Set());
  const [unreadCount, setUnreadCount] = useState(0);

  const ws = useWebSocket({
    onNewMessage: (message) => {
      // 可以触发全局通知
      console.log('收到新消息:', message);

      // 更新未读数量
      setUnreadCount(prev => prev + 1);
    },

    onUserTyping: (data) => {
      setTypingUsers(prev => {
        const newTypingUsers = new Set(prev);
        if (data.is_typing) {
          newTypingUsers.add(data.user_id);
        } else {
          newTypingUsers.delete(data.user_id);
        }
        return newTypingUsers;
      });
    },

    onMemberJoined: (data) => {
      console.log('成员加入群聊:', data);
      // 可以刷新群聊成员列表
    },

    onMemberLeft: (data) => {
      console.log('成员离开群聊:', data);
      // 可以刷新群聊成员列表
    },

    onUserStatusChanged: (data) => {
      console.log('用户状态变化:', data);
      // 可以更新用户在线状态
    },

    onGroupUpdated: (data) => {
      console.log('群聊信息更新:', data);
      // 可以更新群聊信息
    },
  });

  // 当群聊ID变化时，加入/离开相应群聊
  useEffect(() => {
    if (currentGroupId && ws.connected) {
      ws.joinGroup(currentGroupId);
    }

    return () => {
      if (currentGroupId) {
        ws.leaveGroup(currentGroupId);
      }
    };
  }, [currentGroupId, ws.connected]);

  // 防抖处理正在输入状态
  const sendTypingDebounced = useCallback(
    ((delay = 1000) => {
      let timeoutId: NodeJS.Timeout;

      return (isTyping: boolean) => {
        if (timeoutId) {
          clearTimeout(timeoutId);
        }

        if (isTyping) {
          timeoutId = setTimeout(() => {
            ws.sendTyping(currentGroupId!, false);
          }, delay);
        } else {
          ws.sendTyping(currentGroupId!, false);
        }
      };
    })(),
    [ws, currentGroupId]
  );

  return {
    ...ws,
    typingUsers,
    unreadCount,
    sendTypingDebounced,
    setUnreadCount,
  };
};