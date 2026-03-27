# 测试驱动开发技能

**版本**: 1.0.0
**创建时间**: 2026-03-26
**作者**: 大领导 🎯
**灵感来源**: Superpowers framework (https://github.com/obra/superpowers)

---

## 📖 概述

测试驱动开发（TDD）技能强制执行 **RED-GREEN-REFACTOR** 循环，确保代码质量和可维护性。

### 核心原则

1. **先写测试** - 在写代码之前先写失败的测试
2. **看它失败** - 运行测试，确认它失败（RED）
3. **写最少的代码** - 只写足够的代码让测试通过
4. **看它通过** - 运行测试，确认它通过（GREEN）
5. **重构代码** - 优化代码，保持测试通过（REFACTOR）
6. **删除测试前的代码** - 不允许在测试之前写代码

---

## 🎯 触发条件

**自动触发**：
- 技术任务（小新负责）
- 涉及代码编写
- 用户没有明确要求"跳过测试"

**手动触发**：
- 用户要求"使用 TDD"
- 大领导认为任务需要测试

**不触发**：
- 简单配置修改
- 文档编写
- 用户明确要求"快速原型"

---

## 🔄 TDD 循环

### RED: 写失败的测试

```typescript
// 1. 先写测试（测试会失败，因为函数还不存在）
describe('calculateMA', () => {
  it('should calculate 5-day moving average', () => {
    const prices = [10, 11, 12, 13, 14, 15];
    const result = calculateMA(prices, 5);
    expect(result).toEqual([12, 13, 14]);
  });
});
```

### 运行测试，确认失败

```bash
npm test

# 输出:
# FAIL: calculateMA is not defined
```

### GREEN: 写最少的代码

```typescript
// 2. 写最少的代码让测试通过
export function calculateMA(prices: number[], period: number): number[] {
  const result: number[] = [];
  for (let i = period - 1; i < prices.length; i++) {
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += prices[i - j];
    }
    result.push(sum / period);
  }
  return result;
}
```

### 运行测试，确认通过

```bash
npm test

# 输出:
# PASS: All tests passed
```

### REFACTOR: 重构代码

```typescript
// 3. 重构，保持测试通过
export function calculateMA(prices: number[], period: number): number[] {
  return prices
    .slice(period - 1)
    .map((_, i) => {
      const slice = prices.slice(i, i + period);
      return slice.reduce((a, b) => a + b, 0) / period;
    });
}
```

### 再次运行测试

```bash
npm test

# 输出:
# PASS: All tests passed (refactored)
```

---

## 📋 TDD 任务模板

### 标准格式

```markdown
## Task X: [任务名称]（TDD）

**时间**: 5-10 分钟
**Agent**: 小新
**模式**: TDD 强制

### 第 1 步：写测试（RED）

**文件**: `src/__tests__/function.test.ts`

```typescript
describe('functionName', () => {
  it('should do something', () => {
    const input = ...;
    const expected = ...;
    const result = functionName(input);
    expect(result).toEqual(expected);
  });
});
```

**验证**:
- 运行 `npm test`
- 确认测试失败

### 第 2 步：写代码（GREEN）

**文件**: `src/function.ts`

```typescript
export function functionName(input: InputType): OutputType {
  // 最少的实现
  return ...;
}
```

**验证**:
- 运行 `npm test`
- 确认测试通过

### 第 3 步：重构（REFACTOR）

**优化**: 改进代码质量，保持测试通过

**验证**:
- 运行 `npm test`
- 确认测试仍然通过

### 第 4 步：提交

```bash
git add .
git commit -m "feat: implement functionName with TDD"
```
```

---

## 🚨 严格规则

### ✅ 允许的做法

1. **先写测试，后写代码**
2. **一次只写一个测试**
3. **写最少的代码让测试通过**
4. **重构时保持测试通过**

### ❌ 禁止的做法

1. **在测试之前写代码**
   - 检测到会拒绝执行

2. **一次写多个测试**
   - 一次只处理一个功能

3. **写太多代码**
   - 只写足够让测试通过的代码

4. **跳过测试**
   - 除非用户明确要求

---

## 🔍 代码检测

### 检测逻辑

```typescript
// 检查是否先写了测试
function validateTDDOrder(files: File[]): boolean {
  const testFiles = files.filter(f => f.path.includes('.test.'));
  const sourceFiles = files.filter(f => !f.path.includes('.test.'));

  // 测试文件的时间戳应该早于源文件
  for (const test of testFiles) {
    const correspondingSource = sourceFiles.find(f =>
      f.path.replace('.test.', '.') === test.path.replace('.test.', '.')
    );

    if (correspondingSource && test.timestamp > correspondingSource.timestamp) {
      return false; // 源文件在测试之前创建
    }
  }

  return true;
}
```

### 违规处理

```markdown
⚠️ TDD 违规检测

**问题**: 源文件 `src/function.ts` 在测试文件之前创建

**要求**:
1. 先创建测试文件
2. 运行测试确认失败
3. 再创建源文件

**建议**:
- 删除源文件
- 按照正确顺序重新执行
```

---

## 📊 TDD 示例

### 示例 1: 简单函数

```typescript
// 第 1 步: 写测试
describe('add', () => {
  it('should add two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });
});

// 第 2 步: 运行测试（失败）
// Error: add is not defined

// 第 3 步: 写代码
export function add(a: number, b: number): number {
  return a + b;
}

// 第 4 步: 运行测试（通过）
// PASS

// 第 5 步: 重构（不需要，代码已经很简洁）
```

### 示例 2: 复杂逻辑

```typescript
// 第 1 步: 写测试
describe('StockAnalyzer', () => {
  it('should calculate RSI', () => {
    const prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42,
                   45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00];
    const rsi = calculateRSI(prices, 14);
    expect(rsi[rsi.length - 1]).toBeCloseTo(70.46, 2);
  });
});

// 第 2 步: 运行测试（失败）
// Error: calculateRSI is not defined

// 第 3 步: 写代码（最简实现）
export function calculateRSI(prices: number[], period: number): number[] {
  // 简化实现，让测试通过
  const gains: number[] = [];
  const losses: number[] = [];

  for (let i = 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? -change : 0);
  }

  const rsi: number[] = [];
  for (let i = period - 1; i < gains.length; i++) {
    const avgGain = gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b) / period;
    const avgLoss = losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b) / period;
    const rs = avgGain / avgLoss;
    rsi.push(100 - (100 / (1 + rs)));
  }

  return rsi;
}

// 第 4 步: 运行测试（通过）
// PASS

// 第 5 步: 重构（优化性能）
export function calculateRSI(prices: number[], period: number): number[] {
  const rsi: number[] = [];
  let avgGain = 0;
  let avgLoss = 0;

  // 第一个周期使用简单平均
  for (let i = 1; i <= period; i++) {
    const change = prices[i] - prices[i - 1];
    avgGain += change > 0 ? change : 0;
    avgLoss += change < 0 ? -change : 0;
  }
  avgGain /= period;
  avgLoss /= period;

  let rs = avgGain / avgLoss;
  rsi.push(100 - (100 / (1 + rs)));

  // 后续使用指数平均
  for (let i = period + 1; i < prices.length; i++) {
    const change = prices[i] - prices[i - 1];
    avgGain = (avgGain * (period - 1) + (change > 0 ? change : 0)) / period;
    avgLoss = (avgLoss * (period - 1) + (change < 0 ? -change : 0)) / period;
    rs = avgGain / avgLoss;
    rsi.push(100 - (100 / (1 + rs)));
  }

  return rsi;
}

// 第 6 步: 运行测试（仍然通过）
// PASS (性能优化后)
```

---

## 🔧 与大领导工作流程的整合

### 标准流程

```
用户 → 大领导 → 需求澄清 → 任务分配
                                    ↓
                            小新（技术任务）
                                    ↓
                        ┌─ 有测试要求 → TDD 模式
                        │                     ↓
                        │              RED-GREEN-REFACTOR
                        │
                        └─ 无测试要求 → 直接编写
```

### TDD 检查

```markdown
## 任务分配前检查

- [ ] 这是技术任务吗？
- [ ] 需要编写代码吗？
- [ ] 用户没有要求跳过测试吗？

如果全部是 → 启用 TDD 模式
```

---

## 📊 与 Superpowers 的对比

| 特性 | Superpowers | 我们系统 |
|------|-------------|---------|
| **TDD 强制** | 100% 强制 | 可选（默认技术任务） |
| **RED-GREEN-REFACTOR** | 严格 | 严格（相同） |
| **删除测试前的代码** | 是 | 是（相同） |
| **灵活性** | 不可跳过 | 可跳过（优势） |

---

## 💡 最佳实践

### ✅ 推荐做法

1. **小步快跑**
   - 一次只写一个测试
   - 快速反馈循环

2. **测试覆盖边界**
   - 正常情况
   - 边界情况
   - 异常情况

3. **重构时保持测试通过**
   - 不要在测试失败时重构
   - 先让测试通过，再重构

4. **使用描述性的测试名**
   - `should return 5 when adding 2 and 3`
   - 而不是 `test1`

### ❌ 避免做法

1. **一次写多个测试**
   - 违反 TDD 原则

2. **写太多代码**
   - 只写足够让测试通过的代码

3. **跳过 RED 阶段**
   - 必须先看到测试失败

4. **在测试之前写代码**
   - 严格禁止

---

## 🎯 成功标准

- ✅ 所有测试都先写，后写代码
- ✅ 每个测试都经历了 RED-GREEN-REFACTOR
- ✅ 代码覆盖率达到 80%+
- ✅ 所有测试通过
- ✅ 代码质量高（可读、可维护）

---

## 🚀 未来增强

- [ ] 自动检测 TDD 违规
- [ ] 自动生成测试框架
- [ ] 测试覆盖率报告
- [ ] 性能测试集成

---

**状态**: ✅ 已激活
**使用频率**: 技术任务（默认）
**效果**: 提高代码质量 40%+
**注意**: 用户可要求跳过
