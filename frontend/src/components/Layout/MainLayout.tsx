/**
 * Main application layout.
 */

import { useState, useEffect } from 'react';
import {
  Layout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Typography,
  Space,
  message,
  Tag,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  MobileOutlined,
  LogoutOutlined,
  UserOutlined,
  DeleteOutlined,
  HeartFilled,
  RobotOutlined,
  ExperimentOutlined,
  QuestionCircleOutlined,
  SafetyOutlined,
  GithubOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';
import { useSessionStore } from '../../store/sessionStore';
import { ChatPanel } from '../Chat';
import { PhoneView, TakeoverModal } from '../PhoneView';
import { AgentSelector } from '../Settings';
import { HelpModal } from '../Help';
import { ApiError } from '../../services/api';
import type { AgentType } from '../../types';
import styles from './MainLayout.module.css';

const { Header, Sider, Content } = Layout;
const { Text, Link } = Typography;

// Agent 图标映射（与 AgentSelector 保持一致）
const AGENT_ICONS: Record<AgentType, React.ReactNode> = {
  glm: <RobotOutlined />,
  gelab: <ExperimentOutlined />,
};

// Agent 标签映射
const AGENT_LABELS: Record<AgentType, string> = {
  glm: 'AutoGLM',
  gelab: 'StepFun',
};

// Agent 颜色映射
const AGENT_COLORS: Record<AgentType, string> = {
  glm: 'blue',
  gelab: 'green',
};

export function MainLayout() {
  const { user, logout } = useAuthStore();
  const {
    sessions,
    currentSession,
    isCreatingSession,
    selectedAgentType,
    setAgentType,
    fetchSessions,
    createSession,
    selectSession,
    closeSession,
    sendTask,
  } = useSessionStore();

  const [collapsed, setCollapsed] = useState(false);
  const [helpModalOpen, setHelpModalOpen] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handleCreateSession = async () => {
    try {
      const now = new Date();
      const timeStr = `${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
      await createSession(`会话 ${timeStr}`);
      message.success('会话创建成功');
    } catch (error) {
      // Handle session limit errors with friendly messages
      if (error instanceof ApiError && error.status === 403) {
        const detail = error.detail as { type?: string; message?: string; suggestion?: string };
        
        if (detail?.type === 'daily_limit_exceeded') {
          message.error({
            content: (
              <div>
                <div style={{ fontWeight: 500 }}>{detail.message}</div>
                <div style={{ fontSize: 12, marginTop: 4, color: 'rgba(255,255,255,0.65)' }}>
                  ⏰ 明天 00:00 将自动重置配额
                </div>
              </div>
            ),
            duration: 6,
          });
        } else if (detail?.type === 'active_limit_exceeded') {
          message.error({
            content: (
              <div>
                <div style={{ fontWeight: 500 }}>{detail.message}</div>
                {detail.suggestion && (
                  <div style={{ fontSize: 12, marginTop: 4, color: 'rgba(255,255,255,0.65)' }}>
                    💡 {detail.suggestion}
                  </div>
                )}
              </div>
            ),
            duration: 6,
          });
        } else {
          message.error(detail?.message || '创建会话失败');
        }
      } else {
        message.error('资源紧张，创建会话失败，请稍后重试');
      }
    }
  };

  const handleCloseSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await closeSession(sessionId);
      message.success('会话已关闭');
    } catch {
      message.error('关闭会话失败');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      message.error('退出失败');
    }
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.email || '用户',
      disabled: true,
    },
    { type: 'divider' as const },
    {
      key: 'help',
      icon: <QuestionCircleOutlined />,
      label: '使用帮助',
      onClick: () => setHelpModalOpen(true),
    },
    { type: 'divider' as const },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  return (
    <Layout className={styles.layout}>
      {/* Sidebar */}
      <Sider
        width={280}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        className={styles.sider}
        theme="dark"
      >
        <div className={styles.logo}>
          <img src="/logo.png" alt="Remote GUI Automation" className={styles.logoImage} />
          {!collapsed && <span className={styles.logoText}>Remote GUI Automation</span>}
        </div>

        {/* Agent Selector - only show when not collapsed */}
        {!collapsed && (
          <AgentSelector
            value={selectedAgentType}
            onChange={setAgentType}
            disabled={isCreatingSession}
          />
        )}

        <div className={styles.newSession}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateSession}
            loading={isCreatingSession}
            block={!collapsed}
            className={styles.newSessionButton}
          >
            {!collapsed && '新建会话'}
          </Button>
        </div>

        <div className={styles.sessionList}>
          {sessions.length === 0 ? (
            <div className={styles.emptyList}>
              {!collapsed && (
                <Text type="secondary">暂无会话</Text>
              )}
            </div>
          ) : (
            <Menu
              mode="inline"
              selectedKeys={currentSession ? [currentSession.id] : []}
              className={styles.menu}
              items={sessions.map((session) => {
                const agentType = session.agent_type || 'glm';
                const agentIcon = AGENT_ICONS[agentType];
                const agentLabel = AGENT_LABELS[agentType];
                const agentColor = AGENT_COLORS[agentType];
                
                return {
                  key: session.id,
                  icon: agentIcon,
                  label: (
                    <Tooltip
                      title={
                        <div>
                          <div><strong>会话名称：</strong>{session.name || `会话 ${session.id.slice(0, 8)}`}</div>
                          <div><strong>Agent 类型：</strong>{agentLabel} Agent</div>
                          <div><strong>状态：</strong>{session.status === 'active' ? '已连接' : session.status}</div>
                          <div><strong>创建时间：</strong>{new Date(session.created_at).toLocaleString('zh-CN')}</div>
                        </div>
                      }
                      placement="right"
                    >
                      <div className={styles.sessionItem}>
                        <span className={styles.sessionName}>
                          {session.name || `会话 ${session.id.slice(0, 8)}`}
                        </span>
                        <Tag color={agentColor} className={styles.agentTag}>
                          {agentLabel}
                        </Tag>
                        <Button
                          type="text"
                          size="small"
                          icon={<DeleteOutlined />}
                          onClick={(e) => handleCloseSession(session.id, e)}
                          className={styles.deleteButton}
                        />
                      </div>
                    </Tooltip>
                  ),
                  onClick: () => selectSession(session),
                };
              })}
            />
          )}
        </div>
      </Sider>

      {/* Main content */}
      <Layout>
        <Header className={styles.header}>
          <div className={styles.headerLeft}>
            {currentSession && (
              <Space>
                <MobileOutlined />
                <Text strong>
                  {currentSession.name || `会话 ${currentSession.id.slice(0, 8)}`}
                </Text>
                <Tag 
                  color={AGENT_COLORS[currentSession.agent_type || 'glm']} 
                  icon={AGENT_ICONS[currentSession.agent_type || 'glm']}
                >
                  {AGENT_LABELS[currentSession.agent_type || 'glm']} Agent
                </Tag>
                <span
                  className={`${styles.status} ${
                    currentSession.status === 'active' ? styles.active : ''
                  }`}
                >
                  {currentSession.status === 'active' ? '已连接' : currentSession.status}
                </span>
              </Space>
            )}
          </div>

          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div className={styles.userInfo}>
              <Avatar
                src={user?.avatar_url}
                icon={!user?.avatar_url && <UserOutlined />}
                size="small"
              />
              {user?.name && (
                <Text className={styles.userName}>{user.name}</Text>
              )}
            </div>
          </Dropdown>
        </Header>

        <Content className={styles.content}>
          <div className={styles.mainArea}>
            {/* Chat panel */}
            <div id="chat-area" className={styles.chatArea}>
              <ChatPanel onSendMessage={sendTask} />
            </div>

            {/* Phone view */}
            <div className={styles.phoneArea}>
              <PhoneView />
            </div>
          </div>
          
          {/* Acknowledgment footer */}
          <div className={styles.acknowledgment}>
            <div className={styles.acknowledgmentLeft}>
              <HeartFilled className={styles.heartIcon} style={{ fontSize: '18px' }}/>
              <Text className={styles.acknowledgmentText} style={{ fontSize: '16px', fontWeight: 'bold' }}>
                感谢无影
                <Link 
                  href="https://www.aliyun.com/product/agentbay" 
                  target="_blank"
                  className={styles.acknowledgmentLink} style={{ fontSize: '16px', fontWeight: 'bold' }}
                >
                  AgentBay
                </Link>
                团队对于本项目的大力支持
              </Text>
            </div>
            <div className={styles.acknowledgmentCenter}>
              <Link
                href="https://github.com/5101good/rga"
                target="_blank"
                className={styles.githubLink}
              >
                <GithubOutlined className={styles.githubIcon} />
                <Text className={styles.githubText}>GitHub</Text>
                <StarOutlined className={styles.starIcon} />
              </Link>
            </div>
            <div className={styles.disclaimerText}>
              <SafetyOutlined style={{ marginRight: '6px' }} />
              <Text style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.5)' }}>
                仅供个人学习使用，请注意您的信息安全
              </Text>
            </div>
          </div>
        </Content>
      </Layout>

      {/* Takeover modal */}
      <TakeoverModal />

      {/* Help modal */}
      <HelpModal open={helpModalOpen} onClose={() => setHelpModalOpen(false)} />
    </Layout>
  );
}

