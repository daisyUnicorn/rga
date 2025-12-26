/**
 * Login page with Google and GitHub OAuth.
 */

import { Button, Card, Typography, Space } from 'antd';
import { GoogleOutlined, GithubOutlined, StarOutlined } from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';
import styles from './LoginPage.module.css';

const { Title, Text, Link } = Typography;

export function LoginPage() {
  const { login, loginWithGitHub } = useAuthStore();

  const handleGoogleLogin = async () => {
    try {
      await login();
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleGitHubLogin = async () => {
    try {
      await loginWithGitHub();
    } catch (error) {
      console.error('GitHub login failed:', error);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.background}>
        <div className={styles.gradient} />
        <div className={styles.pattern} />
      </div>
      
      <Card className={styles.card} bordered={false}>
        <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
          <div className={styles.logo}>
            <img src="/logo.png" alt="Remote GUI Automation" className={styles.logoImage} />
          </div>

          <div>
            <Title level={2} className={styles.title}>
              Remote GUI Automation
            </Title>
            <Text type="secondary" className={styles.subtitle}>
              AI 驱动的远程 GUI 自动化平台
            </Text>
          </div>
          
          <div className={styles.features}>
            <div className={styles.feature}>
              <span className={styles.featureIcon}>💬</span>
              <span>自然语言控制</span>
            </div>
            <div className={styles.feature}>
              <span className={styles.featureIcon}>📱</span>
              <span>云手机操控</span>
            </div>
            <div className={styles.feature}>
              <span className={styles.featureIcon}>🤖</span>
              <span>智能任务执行</span>
            </div>
          </div>
          
          <div className={styles.loginButtons}>
            <Button
              type="primary"
              size="large"
              icon={<GoogleOutlined />}
              onClick={handleGoogleLogin}
              className={styles.loginButton}
            >
              使用 Google 账号登录
            </Button>

            <Button
              size="large"
              icon={<GithubOutlined />}
              onClick={handleGitHubLogin}
              className={styles.githubButton}
            >
              使用 GitHub 账号登录
            </Button>
          </div>

          <Text type="secondary" className={styles.terms}>
            本项目仅供个人学习使用，不提供任何形式的担保。使用本服务即表示您理解并同意自行承担使用风险
          </Text>
        </Space>
      </Card>
      
      <div className={styles.acknowledgment}>
        <Link 
          href="https://github.com/5101good/rga" 
          target="_blank"
          className={styles.githubProjectLink}
        >
          <GithubOutlined className={styles.githubProjectIcon} />
          <span className={styles.githubProjectText}>开源项目</span>
          <StarOutlined className={styles.githubStarIcon} />
        </Link>
        <Text className={styles.acknowledgmentText}>
          感谢无影
          <Link 
            href="https://www.aliyun.com/product/agentbay" 
            target="_blank"
            className={styles.acknowledgmentLink}
          >
            AgentBay
          </Link>
          团队对于本项目的大力支持
        </Text>
      </div>
    </div>
  );
}

