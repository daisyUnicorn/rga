/**
 * Phone view component for displaying AgentBay cloud phone.
 */

import { useState, useEffect } from 'react';
import { Empty, Spin, Typography, Button, Space, Alert } from 'antd';
import {
  MobileOutlined,
  ReloadOutlined,
  ExpandOutlined,
  CompressOutlined,
} from '@ant-design/icons';
import { useSessionStore } from '../../store/sessionStore';
import styles from './PhoneView.module.css';

const { Text } = Typography;

export function PhoneView() {
  const { currentSession, screenshot } = useSessionStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resourceUrl = currentSession?.resource_url;

  useEffect(() => {
    if (resourceUrl) {
      setIsLoading(true);
      setError(null);
    }
  }, [resourceUrl]);

  const handleIframeLoad = () => {
    setIsLoading(false);
  };

  const handleIframeError = () => {
    setIsLoading(false);
    setError('无法加载手机画面');
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setError(null);
    // Force iframe refresh by updating key
    const iframe = document.querySelector('iframe');
    if (iframe) {
      iframe.src = iframe.src;
    }
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!currentSession) {
    return (
      <div className={styles.container}>
        <Empty
          image={<MobileOutlined className={styles.emptyIcon} />}
          description={
            <Text type="secondary">选择或创建会话以查看手机画面</Text>
          }
        />
      </div>
    );
  }

  if (!resourceUrl) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <Spin size="large" />
          <Text type="secondary" style={{ marginTop: 16 }}>
            正在启动云手机...
          </Text>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${isFullscreen ? styles.fullscreen : ''}`}>
      <div className={styles.header}>
        <Space>
          <MobileOutlined />
          <Text strong>手机画面</Text>
        </Space>
        <Space>
          <Button
            type="text"
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            size="small"
          />
          <Button
            type="text"
            icon={isFullscreen ? <CompressOutlined /> : <ExpandOutlined />}
            onClick={toggleFullscreen}
            size="small"
          />
        </Space>
      </div>

      <div className={styles.phoneFrame}>
        {error ? (
          <Alert
            type="error"
            message={error}
            action={
              <Button size="small" onClick={handleRefresh}>
                重试
              </Button>
            }
          />
        ) : (
          <>
            {isLoading && (
              <div className={styles.loadingOverlay}>
                <Spin size="large" />
              </div>
            )}
            <iframe
              src={resourceUrl}
              className={styles.iframe}
              onLoad={handleIframeLoad}
              onError={handleIframeError}
              allow="fullscreen"
              sandbox="allow-same-origin allow-scripts allow-forms"
            />
          </>
        )}
      </div>

      {/* Fallback: Show screenshot if available */}
      {screenshot && !resourceUrl && (
        <div className={styles.screenshot}>
          <img
            src={`data:image/png;base64,${screenshot.base64}`}
            alt="Phone Screenshot"
            className={styles.screenshotImage}
          />
        </div>
      )}
    </div>
  );
}

