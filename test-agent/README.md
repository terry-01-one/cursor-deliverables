# test-agent

通用测试 Agent：用 YAML 描述用例，执行 HTTP 接口测试，输出 JSON / HTML 报告；也可从 OpenAPI 生成套件骨架。

配合 Cursor Skill `test-agent` 使用：在对话里说「用测试 agent 测这个」即可。

## 安装

```bash
cd ~/Documents/test-agent
python3 -m pip install -r requirements.txt
```

## 快速开始

```bash
# 跑内置示例（访问 httpbin.org）
python3 -m agent run examples/sample_suite.yaml

# 复制一份空白套件
python3 -m agent init examples/my_suite.yaml

# 从 OpenAPI 生成套件
python3 -m agent gen path/to/openapi.yaml -o examples/api_suite.yaml
```

报告默认写到 `reports/`。

## 套件格式

```yaml
name: my-api
base_url: https://api.example.com
timeout: 10
headers:
  Authorization: Bearer YOUR_TOKEN
cases:
  - id: health
    name: 健康检查
    method: GET
    path: /health
    expect:
      status: 200
      contains: ["ok"]
      json_path:
        status: up
```

支持字段：`method` / `path` / `headers` / `query` / `body` / `expect.status` / `expect.contains` / `expect.json_path` / `expect.headers`。

## 边界

- 当前执行器面向 **HTTP API**（通用接口回归）。
- 不包含浏览器 UI、微信小游戏挂机或未授权系统探测。
- UI / 单元测试可在 Cursor Skill 流程里由 Agent 生成代码，再交给本项目做接口回归。
