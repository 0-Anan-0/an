import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, message, Upload, Typography, Tooltip, Modal } from 'antd';
import { SendOutlined, UploadOutlined, ClearOutlined } from '@ant-design/icons';
import { chatHistoryManager } from '../../utils/chatHistory';

const { TextArea } = Input;
const { Title } = Typography;

export type MessageType = {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  content_blocks?: Array<{
    type: string;
    content: string;
  }>;
  references?: Array<{
    id: number;
    text: string;
    source: string;
    page: number;
    chunk_id: number;
    source_info: string;
  }>;
};

type ChatMode = 'text' | 'image' | 'audio' | 'pdf';

interface ChatPageProps {
  mode: ChatMode;
}

const ChatPage: React.FC<ChatPageProps> = ({ mode }) => {
  // 从localStorage加载历史记录
  const [messages, setMessages] = useState<MessageType[]>(() => {
    return chatHistoryManager.getHistory(mode);
  });
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 模态框状态
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentReference, setCurrentReference] = useState<any>(null);

  const modeConfig = {
    text: { title: '智能问答', allowedFileTypes: [] },
    image: { title: '图片分析', allowedFileTypes: ['.jpg', '.jpeg', '.png'] },
    audio: { title: '音频转写', allowedFileTypes: ['.mp3', '.wav'] },
    pdf: { title: 'PDF解析', allowedFileTypes: ['.pdf'] },
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 保存历史记录到localStorage
  useEffect(() => {
    chatHistoryManager.saveHistory(mode, messages);
  }, [messages, mode]);

  const handleClearHistory = () => {
    if (window.confirm('确定要清除所有聊天历史吗？')) {
      setMessages([]);
      chatHistoryManager.clearHistory(mode);
      message.success('聊天历史已清除');
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && !uploadedFile && mode !== 'text') {
      message.warning('请输入消息或上传文件');
      return;
    }

    const userMessage: MessageType = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      role: 'user',
      timestamp: new Date(),
      content_blocks: [
        {
          type: 'text',
          content: inputValue.trim(),
        },
      ],
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsStreaming(true);

    try {
      const formData = new FormData();
      
      // 添加内容块
      const contentBlocks = [
        {
          type: 'text',
          content: inputValue.trim(),
        },
      ];
      formData.append('content_blocks', JSON.stringify(contentBlocks));
      
      // 添加对话历史（转换为后端所需格式）
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        content_blocks: msg.content_blocks || [],
      }));
      formData.append('history', JSON.stringify(history));
      
      // 添加文件（根据模式）
      if (uploadedFile) {
        let fileToSend: File | null = null;
        if (uploadedFile.originFileObj) {
          // Antd Upload组件返回的文件对象，实际文件在originFileObj中
          fileToSend = uploadedFile.originFileObj;
        } else if (uploadedFile instanceof File) {
          // 直接的File对象
          fileToSend = uploadedFile;
        }
        
        if (fileToSend) {
          if (mode === 'image') {
            formData.append('image_file', fileToSend);
          } else if (mode === 'audio') {
            formData.append('audio_file', fileToSend);
          } else if (mode === 'pdf') {
            formData.append('pdf_file', fileToSend);
          }
        }
      }

      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('请求失败');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应');
      }

      const assistantMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: '',
        role: 'assistant',
        timestamp: new Date(),
        references: [],
      };

      setMessages(prev => [...prev, assistantMessage]);

      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataStr = line.slice(5).trim();
            if (dataStr) {
              try {
                const data = JSON.parse(dataStr);
                if (data.type === 'content_delta') {
                  fullResponse += data.content;
                  setMessages(prev => {
                    const updated = [...prev];
                    const last = updated[updated.length - 1];
                    if (last.role === 'assistant') {
                      // 创建副本以符合React不可变性原则
                      const updatedLast = {
                        ...last,
                        content: last.content + data.content,
                      };
                      updated[updated.length - 1] = updatedLast;
                    }
                    return updated;
                  });
                } else if (data.type === 'message_complete') {
                  // 更新完整内容和引用
                  setMessages(prev => {
                    const updated = [...prev];
                    const last = updated[updated.length - 1];
                    if (last.role === 'assistant') {
                      const updatedLast = {
                        ...last,
                        references: data.references || [],
                      };
                      updated[updated.length - 1] = updatedLast;
                    }
                    return updated;
                  });
                  // 消息完成，跳出循环
                  break;
                } else if (data.type === 'error') {
                  throw new Error(data.error);
                }
              } catch (jsonError) {
                console.error('JSON解析错误:', jsonError);
              }
            }
          }
        }
      }
    } catch (error) {
      message.error('请求失败，请稍后重试');
      console.error('Error:', error);
    } finally {
      setIsStreaming(false);
      setUploadedFile(null);
    }
  };

  const handleFileChange = (info: any) => {
    // 文件选择成功后立即保存，不依赖上传状态
    if (info.file) {
      setUploadedFile(info.file);
      message.success(`${info.file.name} 文件上传成功`);
    } else if (info.file.status === 'error') {
      message.error(`${info.file.name} 文件上传失败`);
    }
  };

  // 处理引用点击
  const handleReferenceClick = (reference: NonNullable<MessageType['references']>[0]) => {
    setCurrentReference(reference);
    setIsModalVisible(true);
  };

  // 关闭模态框
  const handleCloseModal = () => {
    setIsModalVisible(false);
    setCurrentReference(null);
  };

  // 将文本中的引用转换为可点击的元素
  const renderContentWithReferences = (content: string, references: MessageType['references'] = []) => {
    if (!references || references.length === 0) {
      return content;
    }

    // 正则表达式匹配引用标记，如[1]、[2]等
    const referencePattern = /\[(\d+)\]/g;
    const result: React.ReactNode[] = [];
    let lastIndex = 0;
    let keyCounter = 0;

    let match;
    while ((match = referencePattern.exec(content)) !== null) {
      // 添加匹配前的文本
      if (match.index > lastIndex) {
        result.push(
          <span key={`text-${keyCounter++}`}>
            {content.slice(lastIndex, match.index)}
          </span>
        );
      }

      // 处理引用
      const refIndex = parseInt(match[1], 10);
      const reference = references.find(ref => ref.id === refIndex);
      
      if (reference) {
        result.push(
          <span
            key={`ref-${keyCounter++}-${refIndex}`}
            className="text-blue-500 cursor-pointer hover:underline ml-1 mr-1"
            onClick={() => handleReferenceClick(reference)}
          >
            [{refIndex}]
          </span>
        );
      } else {
        // 如果找不到对应的引用，显示原始文本
        result.push(
          <span key={`raw-${keyCounter++}`}>
            {match[0]}
          </span>
        );
      }

      lastIndex = match.index + match[0].length;
    }

    // 添加剩余文本
    if (lastIndex < content.length) {
      result.push(
        <span key={`text-${keyCounter++}`}>
          {content.slice(lastIndex)}
        </span>
      );
    }

    return result;
  };

  return (
    <div className="h-screen flex flex-col">
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <Title level={2} className="m-0">{modeConfig[mode].title}</Title>
        <Tooltip title="清除聊天历史">
          <Button
            icon={<ClearOutlined />}
            onClick={handleClearHistory}
            danger
            size="small"
          >
            清除历史
          </Button>
        </Tooltip>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-4 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100 dark:bg-gray-800'}`}
              >
                <p>{renderContentWithReferences(msg.content, msg.references)}</p>
              </div>
            </div>
          ))}
          {isStreaming && (
            <div className="flex justify-start mb-4">
              <div className="max-w-[80%] p-4 rounded-lg bg-gray-100 dark:bg-gray-800">
                <span className="animate-pulse">...</span>
              </div>
            </div>
          )}
          {messages.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p>暂无聊天记录</p>
              <p className="text-sm mt-2">开始对话，探索多模态大模型的能力吧！</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      <footer className="bg-white shadow-inner p-4">
        <div className="max-w-4xl mx-auto">
          {mode !== 'text' && (
            <div className="mb-4">
              <Upload
                beforeUpload={() => false}
                onChange={handleFileChange}
                accept={modeConfig[mode].allowedFileTypes.join(',')}
                showUploadList={false}
              >
                <Button icon={<UploadOutlined />} className="mr-2">
                  上传{mode === 'image' ? '图片' : mode === 'audio' ? '音频' : 'PDF'}
                </Button>
              </Upload>
              {uploadedFile && (
                <span className="text-sm text-gray-500">
                  已上传: {uploadedFile.name}
                </span>
              )}
            </div>
          )}
          
          <div className="flex gap-2">
            <TextArea
              placeholder={`请输入您的问题...`}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPressEnter={() => handleSendMessage()}
              autoSize={{ minRows: 1, maxRows: 4 }}
              className="flex-1"
              disabled={isStreaming}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSendMessage}
              disabled={isStreaming || (!inputValue.trim() && !uploadedFile && mode !== 'text')}
              className="self-end"
            >
              发送
            </Button>
          </div>
        </div>
      </footer>

      {/* 引用详情模态框 */}
      <Modal
        title="引用详情"
        open={isModalVisible}
        onCancel={handleCloseModal}
        footer={[
          <Button key="close" onClick={handleCloseModal}>
            关闭
          </Button>,
        ]}
        width={600}
      >
        {currentReference && (
          <div className="space-y-4">
            <div>
              <strong>引用ID：</strong>{currentReference.id}
            </div>
            <div>
              <strong>文档块ID：</strong>{currentReference.chunk_id}
            </div>
            <div>
              <strong>页码：</strong>{currentReference.page}
            </div>
            <div>
              <strong>来源：</strong>{currentReference.source}
            </div>
            <div>
              <strong>来源信息：</strong>{currentReference.source_info}
            </div>
            <div>
              <strong>原始内容：</strong>
              <div className="mt-2 p-3 bg-gray-50 border rounded">
                {currentReference.text}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ChatPage;
