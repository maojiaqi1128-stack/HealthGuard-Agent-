# 快速上手指南

本指南帮助你从零启动 HealthGuard-Agent 并完成第一次病历分析。

---

## 第一步：环境准备

### 1. 安装 Python 3.11+

```powershell
# 检查版本
python --version
# 若低于 3.11，从 https://www.python.org/downloads/ 安装
```

### 2. 安装 Ollama（本地 LLM 运行时）

访问 https://ollama.com 下载并安装，然后拉取模型：

```powershell
# 拉取 Llama 3（推荐，8B 足够本地运行）
ollama pull llama3:8b

# 可选：拉取 Mistral（更轻量）
ollama pull mistral:7b

# 验证 Ollama 正常运行
ollama list
```

### 3. 安装项目依赖

```powershell
cd E:\HealthGuard-Agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

---

## 第二步：配置环境变量

```powershell
# 复制配置模板
Copy-Item .env.example .env
```

用文本编辑器打开 `.env`，重点修改以下项：

```ini
# Ollama 地址（默认即可，确保 Ollama 正在运行）
OLLAMA_BASE_URL=http://localhost:11434

# 使用已拉取的模型名
OLLAMA_MODEL=llama3:8b

# ChromaDB 数据存放路径
CHROMA_PERSIST_DIR=../data/db/chroma

# 日志级别（开发时用 DEBUG，生产用 INFO）
LOG_LEVEL=DEBUG
```

---

## 第三步：启动 Ollama 服务

**务必先启动 Ollama**，否则项目无法调用 LLM：

```powershell
# 方式一：直接启动（保持这个终端不关闭）
ollama serve

# 方式二：Ollama 安装后会自动以 Windows 服务运行
# 可在任务管理器确认 "ollama" 进程正在运行
```

验证 Ollama 可用：

```powershell
# 简单测试
ollama run llama3:8b "你好，请介绍一下自己"
```

---

## 第四步：初始化 ICD-10 数据

项目内置了常见疾病的 ICD-10 编码样本，运行初始化脚本：

```powershell
.venv\Scripts\Activate.ps1
python scripts/seed_icd_data.py
```

输出示例：

```
正在初始化 ICD-10 数据...
已加载 20 条样本编码
写入 ../data/icd/icd10_sample.csv
ICD-10 数据初始化完成 ✓
```

---

## 第五步：构建医学指南知识库

将医学指南文本文件（.txt 或 .md）放入 `data/guidelines/` 目录，然后运行：

```powershell
python scripts/setup_knowledge_base.py
```

输出示例：

```
正在构建知识库...
已加载 5 个指南文档
ChromaDB 向量化完成，共 247 个片段
知识库路径：../data/db/chroma
知识库构建完成 ✓
```

> **提示**：若没有现成指南文件，项目会在 `data/guidelines/sample_guidelines/` 下自动生成 3 份示例指南供测试。

---

## 第六步：启动 API 服务

```powershell
python -m healthguard.main
```

成功启动后，终端显示：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     LangGraph 工作流已编译，Agent 系统就绪 ✓
```

此时可以访问：
- **API 文档（交互式）**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health

---

## 第七步：进行第一次病历分析

### 方式一：通过 Swagger UI（推荐新手）

1. 浏览器打开 http://localhost:8000/docs
2. 找到 `POST /api/v1/analyze` 端点，点击 "Try it out"
3. 输入以下示例病历：

```json
{
  "note_text": "患者男性，72岁，因间歇性胸痛2周入院。疼痛位于胸骨后，劳累时加重，休息后缓解。既往高血压病史10年，吸烟史40年。查体：BP 150/95 mmHg，心率82次/分，律齐。心电图示V1-V4导联ST段压低0.1mV。心肌酶：CK-MB 35 U/L，cTnI 0.8 ng/mL（参考值<0.04）。初步诊断：冠心病，不稳定型心绞痛。",
  "patient_id": "P2026043001",
  "include_evidence": true
}
```

4. 点击 "Execute"，等待约 30-60 秒
5. 查看返回结果

### 方式二：通过 curl / PowerShell

```powershell
$body = @{
    note_text = "患者女性，65岁，2型糖尿病史15年，近期出现双下肢水肿，尿蛋白+++，血肌酐 180 μmol/L。眼科检查：糖尿病视网膜病变（背景期）。BP 145/90 mmHg。初步诊断：糖尿病肾病。"
    patient_id = "P2026043002"
    include_evidence = $true
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analyze" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### 方式三：运行内置 Demo 脚本

```powershell
python scripts/run_demo.py
```

---

## 返回结果说明

一次完整的分析返回如下结构：

```json
{
  "patient_id": "P2026043001",
  "status": "completed",
  "structured_data": {
    "年龄": "72岁",
    "性别": "男性",
    "主诉": "间歇性胸痛2周",
    "诊断": ["冠心病", "不稳定型心绞痛"],
    "ICD编码": [
      {"疾病": "冠心病", "ICD-10": "I25.9"},
      {"疾病": "不稳定型心绞痛", "ICD-10": "I20.0"}
    ]
  },
  "retrieved_guidelines": [
    {
      "标题": "中国稳定性冠心病诊断与治疗指南（2024）",
      "相关度": 0.87,
      "建议摘要": "对于稳定性冠心病患者，推荐β受体阻滞剂作为一线治疗..."
    }
  ],
  "safety_check": {
    "幻觉风险": "低",
    "事实一致性": "高",
    "需人工审核": false
  },
  "processing_time_seconds": 42.3
}
```

---

## 常见问题排查

### Q: 启动时报 `ConnectionRefusedError: Ollama`

**原因**：Ollama 未启动或端口不对。
**解决**：
```powershell
# 确认 Ollama 进程存在
Get-Process ollama
# 若没有，手动启动
ollama serve
```

### Q: 分析超时（> 120秒）

**原因**：LLM 响应慢，或模型未正确加载。
**解决**：
```powershell
# 换用更轻量的模型
# 修改 .env 中 OLLAMA_MODEL=mistral:7b
# 重启服务
```

### Q: ChromaDB 报错 `persist directory not found`

**原因**：知识库未初始化。
**解决**：
```powershell
python scripts/setup_knowledge_base.py
```

### Q: Windows 上 `Activate.ps1` 被策略阻止

**解决**（以管理员运行 PowerShell）：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 下一步

- 阅读 `docs/architecture.md` 了解系统架构
- 阅读 `docs/api_reference.md` 了解所有 API 端点
- 将项目推送到 GitHub：
  ```powershell
  git init
  git add .
  git commit -m "feat: initial HealthGuard-Agent"
  git remote add origin https://github.com/你的用户名/HealthGuard-Agent.git
  git push -u origin main
  ```
