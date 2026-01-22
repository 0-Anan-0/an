import type { MessageType } from '../pages/ChatPage';

class ChatHistoryManager {
  private readonly storageKeyPrefix = 'chat_history_';

  /**
   * 检查是否在浏览器环境中
   */
  private isBrowser(): boolean {
    return typeof window !== 'undefined';
  }

  /**
   * 获取指定模式的聊天历史
   */
  getHistory(mode: string): MessageType[] {
    if (!this.isBrowser()) {
      return [];
    }
    
    const key = `${this.storageKeyPrefix}${mode}`;
    const stored = localStorage.getItem(key);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        // 将字符串日期转换为Date对象
        return parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
      } catch (error) {
        console.error('解析聊天历史失败:', error);
        return [];
      }
    }
    return [];
  }

  /**
   * 保存聊天历史
   */
  saveHistory(mode: string, history: MessageType[]): void {
    if (!this.isBrowser()) {
      return;
    }
    
    const key = `${this.storageKeyPrefix}${mode}`;
    try {
      localStorage.setItem(key, JSON.stringify(history));
    } catch (error) {
      console.error('保存聊天历史失败:', error);
    }
  }

  /**
   * 清除指定模式的聊天历史
   */
  clearHistory(mode: string): void {
    if (!this.isBrowser()) {
      return;
    }
    
    const key = `${this.storageKeyPrefix}${mode}`;
    localStorage.removeItem(key);
  }

  /**
   * 清除所有聊天历史
   */
  clearAllHistory(): void {
    if (!this.isBrowser()) {
      return;
    }
    
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith(this.storageKeyPrefix)) {
        localStorage.removeItem(key);
      }
    });
  }
}

export const chatHistoryManager = new ChatHistoryManager();
