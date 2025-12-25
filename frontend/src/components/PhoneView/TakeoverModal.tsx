/**
 * Takeover modal for human intervention.
 */

import { Modal, Typography, Button, Space, Alert } from 'antd';
import { ExclamationCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useSessionStore } from '../../store/sessionStore';
import styles from './TakeoverModal.module.css';

const { Title, Text, Paragraph } = Typography;

export function TakeoverModal() {
  const { takeover, completeTakeover, stopTask } = useSessionStore();

  const handleComplete = () => {
    completeTakeover();
  };

  const handleStop = () => {
    stopTask();
    // Also close the takeover modal since the task is being stopped
    completeTakeover();
  };

  return (
    <Modal
      open={takeover.isActive}
      footer={null}
      closable={false}
      centered
      width={480}
      className={styles.modal}
      rootClassName={styles.modalRoot}
      getContainer={() => document.getElementById('chat-area') || document.body}
    >
      <div className={styles.content}>
        <div className={styles.icon}>
          <ExclamationCircleOutlined />
        </div>

        <Title level={4} className={styles.title}>
          需要人工接管
        </Title>

        <Alert
          type="warning"
          showIcon={false}
          message={takeover.message || '请在手机画面中完成必要的操作'}
          className={styles.alert}
        />

        <Paragraph type="secondary" className={styles.description}>
          AI 助手遇到了需要您手动处理的情况（如登录、验证码等）。
          请在右侧手机画面中完成操作，然后点击下方按钮继续。
        </Paragraph>

        <div className={styles.steps}>
          <div className={styles.step}>
            <span className={styles.stepNumber}>1</span>
            <Text>在手机画面中完成所需操作</Text>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNumber}>2</span>
            <Text>确认操作已完成</Text>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNumber}>3</span>
            <Text>点击按钮让 AI 继续执行</Text>
          </div>
        </div>

        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Button
            type="primary"
            size="large"
            icon={<CheckCircleOutlined />}
            onClick={handleComplete}
            block
            className={styles.completeButton}
          >
            我已完成操作，继续执行
          </Button>
          <Button
            size="large"
            onClick={handleStop}
            block
          >
            停止任务
          </Button>
        </Space>
      </div>
    </Modal>
  );
}

