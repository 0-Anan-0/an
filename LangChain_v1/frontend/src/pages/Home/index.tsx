import React from 'react';
import { Card, Row, Col, Typography } from 'antd';
import { Link } from 'react-router';

const { Title, Text } = Typography;

const Home: React.FC = () => {
  const features = [
    {
      title: '智能问答',
      description: '与大模型进行纯文本对话',
      path: '/chat/text',
      icon: '💬',
    },
    {
      title: '图片分析',
      description: '上传图片，让模型分析图片内容',
      path: '/chat/image',
      icon: '🖼️',
    },
    {
      title: '音频转写',
      description: '上传音频，模型转写并回答相关问题',
      path: '/chat/audio',
      icon: '🎵',
    },
    {
      title: 'PDF解析',
      description: '上传PDF，模型基于PDF内容回答问题',
      path: '/chat/pdf',
      icon: '📄',
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <Title level={1} className="mb-4">多模态大模型RAG系统</Title>
        <Text className="text-gray-600 text-lg">
          基于先进大模型技术，支持多种模态交互的智能问答系统
        </Text>
      </div>
      
      <Row gutter={[16, 16]}>
        {features.map((feature, index) => (
          <Col key={index} xs={24} sm={12} md={6}>
            <Link to={feature.path} className="block hover:no-underline">
              <Card 
                hoverable 
                className="h-full transition-all duration-300 hover:shadow-lg"
              >
                <div className="text-center">
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <Title level={3} className="mb-2">{feature.title}</Title>
                  <Text className="text-gray-500">{feature.description}</Text>
                </div>
              </Card>
            </Link>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default Home;
