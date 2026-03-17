/**
 * auto-cluster.js - 自动聚类机制
 * 
 * 功能: 自动聚类相关模式，生成新的 Skill
 */

const fs = require('fs');
const path = require('path');

// 配置
const PAI_DIR = path.join(process.cwd(), '.pai-learning');
const CONFIDENCE_FILE = path.join(PAI_DIR, 'confidence/scores.json');
const SKILLS_DIR = path.join(process.cwd(), '.claw/skills');

// 加载置信度评分
function loadConfidenceScores() {
  try {
    const content = fs.readFileSync(CONFIDENCE_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    return [];
  }
}

// 聚类相似模式
function clusterPatterns(patterns) {
  const clusters = {};
  
  patterns.forEach(pattern => {
    // 简单的关键词聚类
    const keywords = pattern.name.toLowerCase().split(/[\s\-]+/);
    
    keywords.forEach(keyword => {
      if (keyword.length < 3) return; // 忽略太短的词
      
      if (!clusters[keyword]) {
        clusters[keyword] = [];
      }
      
      clusters[keyword].push(pattern);
    });
  });
  
  return clusters;
}

// 生成新的 Skill
function generateSkill(cluster, keyword) {
  // 计算平均置信度
  const avgConfidence = cluster.reduce((sum, p) => sum + p.confidence, 0) / cluster.length;
  
  // 只生成高置信度的 Skill
  if (avgConfidence < 70) {
    return null;
  }
  
  const skillName = keyword.charAt(0).toUpperCase() + keyword.slice(1);
  
  return {
    name: skillName,
    description: `从 ${cluster.length} 个相关模式聚类而来`,
    confidence: avgConfidence.toFixed(1),
    patterns: cluster.map(p => ({
      name: p.name,
      confidence: p.confidence
    }))
  };
}

// 主函数
function main() {
  console.log('🔄 自动聚类机制');
  console.log('='.repeat(50));
  
  // 加载置信度评分
  const patterns = loadConfidenceScores();
  
  if (patterns.length === 0) {
    console.log('⚠️  没有学习模式可以聚类');
    return;
  }
  
  // 聚类模式
  const clusters = clusterPatterns(patterns);
  
  console.log(`\n📊 发现 ${Object.keys(clusters).length} 个聚类:\n`);
  
  // 生成 Skills
  const skills = [];
  
  Object.entries(clusters).forEach(([keyword, cluster]) => {
    if (cluster.length >= 2) { // 至少 2 个模式才聚类
      const skill = generateSkill(cluster, keyword);
      
      if (skill) {
        skills.push(skill);
        console.log(`✨ ${skill.name}`);
        console.log(`   置信度: ${skill.confidence}`);
        console.log(`   模式数量: ${skill.patterns.length}`);
      }
    }
  });
  
  if (skills.length === 0) {
    console.log('⚠️  没有生成新的 Skill');
  } else {
    console.log(`\n✅ 生成 ${skills.length} 个新 Skill`);
    
    // 保存到文件
    const outputDir = path.join(PAI_DIR, 'skills');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const outputFile = path.join(outputDir, `auto-clustered-${Date.now()}.json`);
    fs.writeFileSync(outputFile, JSON.stringify(skills, null, 2));
    console.log(`💾 已保存: ${outputFile}`);
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('✅ 自动聚类完成\n');
}

// 运行
main();
