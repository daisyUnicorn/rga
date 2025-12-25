/**
 * Agent type selector component.
 */

import { Radio, Space, Typography, Tooltip } from 'antd';
import { RobotOutlined, ExperimentOutlined } from '@ant-design/icons';
import type { AgentType } from '../../types';
import { AGENT_OPTIONS } from '../../types';
import styles from './AgentSelector.module.css';

const { Text } = Typography;

interface AgentSelectorProps {
  value: AgentType;
  onChange: (agentType: AgentType) => void;
  disabled?: boolean;
}

const AGENT_ICONS: Record<AgentType, React.ReactNode> = {
  glm: <RobotOutlined />,
  gelab: <ExperimentOutlined />,
};

export function AgentSelector({ value, onChange, disabled }: AgentSelectorProps) {
  return (
    <div className={styles.container}>
      <Text className={styles.label}>Agent 类型</Text>
      <Radio.Group
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={styles.radioGroup}
      >
        <Space direction="vertical" size="small">
          {AGENT_OPTIONS.map((option) => (
            <Tooltip
              key={option.value}
              title={option.description}
              placement="right"
            >
              <Radio value={option.value} className={styles.radioOption}>
                <Space size="small">
                  {AGENT_ICONS[option.value]}
                  <span>{option.label}</span>
                </Space>
              </Radio>
            </Tooltip>
          ))}
        </Space>
      </Radio.Group>
    </div>
  );
}
