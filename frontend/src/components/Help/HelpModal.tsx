/**
 * Help documentation modal component.
 */

import { Modal, Tabs, Typography, Space, List } from 'antd';
import {
  RocketOutlined,
  RobotOutlined,
  ExperimentOutlined,
  MessageOutlined,
  MobileOutlined,
  SettingOutlined,
  SafetyOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import styles from './HelpModal.module.css';

const { Title, Paragraph, Text, Link } = Typography;

interface HelpModalProps {
  open: boolean;
  onClose: () => void;
}

export function HelpModal({ open, onClose }: HelpModalProps) {
  const tabItems = [
    {
      key: 'quickstart',
      label: (
        <span>
          <RocketOutlined /> 快速开始
        </span>
      ),
      children: (
        <div className={styles.content}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <Title level={4}>欢迎使用 Remote GUI Automation</Title>
              <Paragraph>
                这是一个 AI 驱动的远程 GUI 自动化平台，让您能够通过自然语言控制云手机，实现智能任务执行，体验最新的各种GUI Agent的实际效果。
              </Paragraph>
            </div>

            <div>
              <Title level={5}>
                <RocketOutlined /> 三步快速上手
              </Title>
              <List
                dataSource={[
                  {
                    title: '1. 选择 Agent 类型',
                    description: '在左侧边栏选择您想使用的 AI 智能体类型（AutoGLM 或 StepFun）',
                  },
                  {
                    title: '2. 创建会话',
                    description: '点击"新建会话"按钮，系统将自动为您创建一个云手机环境',
                  },
                  {
                    title: '3. 发送任务',
                    description: '在对话框中用自然语言描述您的任务，AI 将自动执行',
                  },
                ]}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      title={<Text strong>{item.title}</Text>}
                      description={item.description}
                    />
                  </List.Item>
                )}
              />
            </div>

            <div>
              <Title level={5}>
                <MessageOutlined /> 任务示例
              </Title>
              <Paragraph>
                您可以尝试以下任务指令：
              </Paragraph>
              <ul className={styles.exampleList}>
                <li><Text code>打开设置，找到关于手机</Text></li>
                <li><Text code>在应用商店搜索"微信"</Text></li>
                <li><Text code>打开相机拍一张照片</Text></li>
                <li><Text code>查看最近的通知</Text></li>
              </ul>
            </div>
            <Paragraph type="warning">
                <SafetyOutlined /> 本项目仅供<Text strong>个人学习</Text>使用，不提供任何形式的担保和售后服务。项目本身不会采集您的个人信息，但使用过程中依赖第3方的模型和云服务，请不要填写任何个人敏感信息，不要登录银行、交易、社交媒体等App账号，不得用于非法用途。
                使用本服务即表示您理解并同意自行承担使用风险，如因使用本服务造成任何损失，本项目不承担任何责任。
              </Paragraph>
          </Space>
        </div>
      ),
    },
    {
      key: 'agents',
      label: (
        <span>
          <RobotOutlined /> Agent 类型
        </span>
      ),
      children: (
        <div className={styles.content}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <Title level={4}>选择您喜欢的 Agent 类型</Title>
              <Paragraph>
                系统当前提供两种 AI 智能体，您可以按需选择（感谢以下厂商的优秀工作和无私开源）：
              </Paragraph>
            </div>

            <div className={styles.agentCard}>
              <div className={styles.agentHeader}>
                <RobotOutlined className={styles.agentIcon} style={{ color: '#1890ff' }} />
                <div>
                  <Title level={5} style={{ margin: 0 }}>
                    AutoGLM Agent 
                  </Title>
                  <Text type="secondary">基于 AutoGLM-Phone-9B 模型，详情：<Link href="https://github.com/zai-org/Open-AutoGLM" target="_blank">https://github.com/zai-org/Open-AutoGLM</Link>  </Text>
                </div>
              </div>
              <Paragraph>
                <Text strong>特点：</Text>
                <ul>
                  <li>更强的推理和思考能力</li>
                  <li>支持用户介入接管</li>
                </ul>
              </Paragraph>
            </div>

            <div className={styles.agentCard}>
              <div className={styles.agentHeader}>
                <ExperimentOutlined className={styles.agentIcon} style={{ color: '#52c41a' }} />
                <div>
                  <Title level={5} style={{ margin: 0 }}>
                    StepFun Agent 
                  </Title>
                  <Text type="secondary">基于 GELab-Zero-4B-preview 模型，详情：<Link href="https://github.com/stepfun-ai/gelab-zero" target="_blank">https://github.com/stepfun-ai/gelab-zero</Link></Text>
                </div>
              </div>
              <Paragraph>
                <Text strong>特点：</Text>
                <ul>
                  <li>模型体积小，推理速度更快，部署方便</li>
                  <li>开源Agent更完整，支持多设备任务分发、MCP等</li>
                </ul>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>
                <BulbOutlined /> 更多模型与Agent支持接入中，敬请期待。。。
              </Title>
              <List
                size="small"
                dataSource={[
                  'QWen 系列视觉模型',
                  'UI-TARS',
                  'Claude Computer Use',
                  'OpenAI CUA',
                ]}
                renderItem={(item) => (
                  <List.Item>
                    <Text>• {item}</Text>
                  </List.Item>
                )}
              />
            </div>
          </Space>
        </div>
      ),
    },
    {
      key: 'features',
      label: (
        <span>
          <MobileOutlined /> 功能介绍
        </span>
      ),
      children: (
        <div className={styles.content}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <Title level={4}>核心功能</Title>
            </div>

            <div>
              <Title level={5}>
                <MessageOutlined /> 智能对话
              </Title>
              <Paragraph>
                在对话框中使用自然语言描述任务，AI 会自动理解并执行：
              </Paragraph>
              <ul className={styles.featureList}>
                <li>支持中文指令</li>
                <li>理解复杂的多步骤任务</li>
                <li>实时显示 AI 的思考过程</li>
                <li>展示每一步的执行动作</li>
              </ul>
            </div>

            <div>
              <Title level={5}>
                <MobileOutlined /> 云手机实时预览
              </Title>
              <Paragraph>
                右侧基于无影AgentBay云手机沙箱产品，实时显示云手机界面：
              </Paragraph>
              <ul className={styles.featureList}>
                <li>实时同步手机流式画面</li>
                <li>查看 AI 的操作过程</li>
                <li>支持手动接管控制（Takeover）</li>
                <li>随时了解任务执行状态</li>
              </ul>
            </div>

            <div>
              <Title level={5}>
                <SettingOutlined /> 会话管理
              </Title>
              <Paragraph>
                灵活的会话管理功能：
              </Paragraph>
              <ul className={styles.featureList}>
                <li>创建多个独立的会话</li>
                <li>每个会话可使用不同的 Agent</li>
                <li>随时切换或关闭会话</li>
                <li>自动保存对话历史</li>
                <li>会话中的云手机可能会失效过期，请您手动删除会话重建即可</li>
              </ul>
            </div>

            <div>
              <Title level={5}>
                <RobotOutlined /> 执行过程透明化
              </Title>
              <Paragraph>
                完整展示 AI 的执行过程：
              </Paragraph>
              <ul className={styles.featureList}>
                <li><Text strong>思考阶段：</Text>显示 AI 如何理解和规划任务</li>
                <li><Text strong>执行阶段：</Text>展示具体的操作步骤</li>
                <li><Text strong>时间统计：</Text>记录每个阶段的耗时</li>
                <li><Text strong>结果反馈：</Text>任务完成后给出执行结果</li>
              </ul>
            </div>
          </Space>
        </div>
      ),
    },
    {
      key: 'tips',
      label: (
        <span>
          <BulbOutlined /> 使用技巧
        </span>
      ),
      children: (
        <div className={styles.content}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <Title level={4}>
                <BulbOutlined /> 高效使用技巧
              </Title>
            </div>

            <div>
              <Title level={5}>📝 任务描述要清晰</Title>
              <Paragraph>
                <Text strong>好的示例：</Text>
                <ul className={styles.tipList}>
                  <li><Text code>打开设置，进入关于手机页面</Text></li>
                  <li><Text code>在应用商店搜索"网易云音乐"并查看详情</Text></li>
                </ul>
              </Paragraph>
              <Paragraph>
                <Text strong type="warning">需要改进：</Text>
                <ul className={styles.tipList}>
                  <li><Text delete>打开那个</Text>（指代不明确）</li>
                  <li><Text delete>帮我操作一下</Text>（目标不清晰）</li>
                </ul>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>⏰ 等待任务完成</Title>
              <Paragraph>
                • AI 执行任务需要时间，特别是复杂任务<br />
                • 观察对话区域的思考和执行过程<br />
                • 等待任务完成标志或错误提示<br />
                • 不要在任务执行中途发送新任务
              </Paragraph>
            </div>

            <div>
              <Title level={5}>🔄 利用多会话</Title>
              <Paragraph>
                • 为不同类型的任务创建不同的会话<br />
                • 对比不同 Agent 的表现<br />
                • 保留重要会话的历史记录<br />
                • 及时关闭不需要的会话以释放资源
              </Paragraph>
            </div>

            <div>
              <Title level={5}>👁️ 观察执行过程</Title>
              <Paragraph>
                • 右侧实时查看手机屏幕<br />
                • 左侧查看 AI 的思考和动作<br />
                • 注意每个步骤的执行时间<br />
                • 如发现异常及时关闭会话重试
              </Paragraph>
            </div>

            <div>
              <Title level={5}>🎯 合理设置任务目标</Title>
              <Paragraph>
                • 将复杂任务拆分为多个简单任务<br />
                • 每次专注于一个明确的目标<br />
                • 任务完成后再继续下一个<br />
                • 避免一次性描述过多步骤
              </Paragraph>
            </div>
          </Space>
        </div>
      ),
    },
    {
      key: 'faq',
      label: (
        <span>
          <SafetyOutlined /> 常见问题
        </span>
      ),
      children: (
        <div className={styles.content}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <Title level={4}>常见问题解答</Title>
            </div>

            <div><Title level={5}>❓ 什么是无影AgentBay？</Title>
              <Paragraph>
                无影AgentBay是阿里云推出的一款专为AI Agent设计的工具沙箱产品，支持多种操作系统环境，支持实时画面渲染和用户交互。本服务的云手机环境基于无影AgentBay构建。
                详情：<Link href="https://www.aliyun.com/product/agentbay" target="_blank">https://www.aliyun.com/product/agentbay</Link>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>❓ 为什么创建会话失败？</Title>
              <Paragraph>
                可能的原因：
                <ul>
                  <li>云资源暂时紧张，可以多试几次，如果频繁失败，请等待30秒后再重试</li>
                  <li>网络连接问题，检查网络状态</li>
                  <li>已达到同时会话上限，关闭一些不用的会话</li>
                </ul>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>❓ AI 没有正确执行任务？</Title>
              <Paragraph>
                解决方案：
                <ul>
                  <li>检查任务描述是否清晰明确</li>
                  <li>尝试将复杂任务拆分为简单步骤</li>
                  <li>查看 AI 的思考过程，了解理解是否正确</li>
                  <li>尝试更换 Agent 类型</li>
                </ul>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>❓ 会话连接断开了？</Title>
              <Paragraph>
                处理方法：
                <ul>
                  <li>检查网络连接是否稳定</li>
                  <li>刷新页面重新登录</li>
                  <li>删除异常会话，创建新会话</li>
                  <li>如果云手机连接不上，提示authCode过期，请删除会话并新建</li>
                </ul>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>❓ 如何提高任务成功率？</Title>
              <Paragraph>
                建议：
                <ul>
                  <li>使用清晰、具体的任务描述</li>
                  <li>选择合适的 Agent 类型</li>
                  <li>避免过于复杂的任务</li>
                  <li>等待当前任务完成后再发送新任务</li>
                  <li>观察 AI 的执行过程，及时调整策略</li>
                </ul>
              </Paragraph>
            </div>

            <div>
              <Title level={5}>❓ 这是生产环境吗？</Title>
              <Paragraph type="warning">
                <SafetyOutlined /> 本项目仅供<Text strong>个人学习</Text>使用，不提供任何形式的担保和售后服务。项目本身不会采集您的个人信息，使用过程中依赖第3方的模型和云服务，请不要填写任何个人敏感信息，不要登录银行、交易、社交媒体等App账号，不得用于非法用途。
                使用本服务即表示您理解并同意自行承担使用风险，如因使用本服务造成任何损失，本项目不承担任何责任。
              </Paragraph>
            </div>

          </Space>
        </div>
      ),
    },
  ];

  return (
    <Modal
      title="使用帮助"
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      className={styles.modal}
    >
      <Tabs items={tabItems} className={styles.tabs} />
    </Modal>
  );
}

