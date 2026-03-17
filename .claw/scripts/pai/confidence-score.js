/**
 * 置信度评分系统
 * 
 * 功能: 为学习模式计算置信度评分（0-100）
 */

const fs = require('fs');
const path = require('path');

// 配置
const PAI_DIR = path.join(process.cwd(), '.pai-learning');
const SIGNALS_FILE = path.join(PAI_DIR, 'signals/2026-03-17-signals.jsonl');
const CONFIDENCE_FILE = path.join(PAI_DIR, 'confidence/scores.json');

// 置信度评分算法
function calculateConfidence(pattern) {
  let score = 50; // 基础分
  
  // 因素 1: 成功率（30 分）
  if (pattern.success) {
    score += 30;
  }
  
  // 因素 2: 出现频率（20 分）
  const frequency = pattern.frequency || 1;
  score += Math.min(frequency * 5, 20);
  
  // 因素 3: 时间新鲜度（10 分）
  const daysSince = pattern.daysSince || 0;
  if (daysSince < 7) {
    score += 10;
  } else if (daysSince < 30) {
    score += 5;
  }
  
  // 因素 4: 复杂度匹配（10 分）
  if (pattern.complexity && pattern.complexity >= 3) {
    score += 10;
  }
  
  // 因素 5: 情感得分（10 分）
  if (pattern.emotion === 'positive') {
    score += 10;
  } else if (pattern.emotion === 'neutral') {
    score += 5;
  }
  
  // 确保分数在 0-100 范围内
  return Math.max(0, Math.min(100, score));
}

// 加载学习信号
function loadSignals() {
  try {
    const content = fs.readFileSync(SIGNALS_FILE, 'utf-8');
    const lines = content.trim().split('\n');
    
    return lines.map(line => {
      try {
        return JSON.parse(line);
      } catch (error) {
        return null;
      }
    }).filter(p => p !== null);
  } catch (error) {
    return [];
  }
}

// 计算所有模式的置信度
function calculateAllConfidence() {
  const signals = loadSignals();
  
  // 按任务类型分组
  const grouped = {};
  signals.forEach(signal => {
    const key = signal.task_type || signal.type || 'unknown';
    if (!grouped[key]) {
      grouped[key] = {
        count: 0,
        success: 0,
        totalComplexity: 0,
        emotion: 'neutral'
      };
    }
    
    grouped[key].count++;
    if (signal.success) {
      grouped[key].success++;
    }
    grouped[key].totalComplexity += signal.complexity || 0;
    
    if (signal.emotion) {
      grouped[key].emotion = signal.emotion;
    }
  });
  
  // 计算每个模式的置信度
  const results = [];
  
  Object.entries(grouped).forEach(([key, data]) => {
    const pattern = {
      name: key,
      frequency: data.count,
      success: data.success > 0,
      successRate: data.success / data.count,
      complexity: data.totalComplexity / data.count,
      emotion: data.emotion,
      daysSince: 0, // 简化处理
      confidence: 0
    };
    
    pattern.confidence = calculateConfidence(pattern);
    results.push(pattern);
  });
  
  // 按置信度排序
  results.sort((a, b) => b.confidence - a.confidence);
  
  return results;
}

// 主函数
function main() {
  console.log('🎯 置信度评分系统');
  console.log('='.repeat(50));
  
  // 计算置信度
  const results = calculateAllConfidence();
  
  console.log(`\n📊 学习模式置信度 (${results.length} 个模式):\n`);
  
  results.forEach((result, index) => {
    const level = result.confidence >= 80 ? '🟢 高' : result.confidence >= 50 ? '🟡 中' : '🔴 低';
    console.log(`${index + 1}. ${result.name}`);
    console.log(`   置信度: ${result.confidence} ${level}`);
    console.log(`   频率: ${result.frequency}, 成功率: ${(result.successRate * 100).toFixed(0)}%`);
  });
  
  // 保存结果
  const outputDir = path.dirname(CONFIDENCE_FILE);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  fs.writeFileSync(CONFIDENCE_FILE, JSON.stringify(results, null, 2));
  console.log(`\n✅ 置信度评分已保存: ${CONFIDENCE_FILE}`);
  
  // 统计
  const highConfidence = results.filter(r => r.confidence >= 80).length;
  const mediumConfidence = results.filter(r => r.confidence >= 50 && r.confidence < 80).length;
  const lowConfidence = results.filter(r => r.confidence < 50).length;
  
  console.log('\n📈 统计:');
  console.log(`   高置信度 (80-100): ${highConfidence}`);
  console.log(`   中置信度 (50-79):  ${mediumConfidence}`);
  console.log(`   低置信度 (0-49):  ${lowConfidence}`);
  
  console.log('\n' + '='.repeat(50));
  console.log('✅ 置信度评分完成\n');
}

// 运行
main();
