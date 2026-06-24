# ai-servant

`ai-servant` 是面向 Claude CLI 的无人值守任务启动器。它读取一份 YAML 配置文件，加载配置中声明的 Markdown 任务、规则和技能文件，拼接成完整指令后调用 Claude CLI，并把 Claude CLI 的输出透传到标准输出。

## 项目结构

```text
ai_servant/
├── src/              # CLI 入口、配置读取、Markdown 拼接、Claude CLI 调用
├── tests/            # 单元测试
├── update.bat        # Windows：创建 venv 并安装依赖
├── update.sh         # POSIX：创建 venv 并安装依赖
├── test.bat          # Windows：运行测试
└── test.sh           # POSIX：运行测试
```

## 命令行参数

`ai-servant config.yaml`

| 长参数 | 短参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| config | | 文件路径 | ✓ | | YAML 配置文件 |

也可以在仓库根目录使用 `python src config.yaml`。

## 配置文件

```yaml
cwd: .
model: sonnet

tasks:
  - tasks/fix-login.md

rules:
  - rules/base.md
  - rules/no-question.md

skills:
  - skills/python.md
  - skills/testing.md
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `cwd` | 目录路径 | | config 所在目录 | Claude CLI 的运行目录 |
| `model` | 模型名 | | | Claude CLI 当前 session 使用的模型 |
| `tasks` | 多个文件路径 | ✓ | | 任务要求 Markdown；至少一项 |
| `rules` | 多个文件路径 | ✓ | | 规则 Markdown；可为空列表 |
| `skills` | 多个文件路径 | ✓ | | 技能 Markdown；可为空列表 |

`tasks`、`rules`、`skills` 的相对路径始终按 config 文件所在目录解析。`cwd` 只影响 Claude CLI 的工作目录。

配置 `model` 时，`ai-servant` 调用 `claude --model <model> --print`；未配置时调用 `claude --print`。

## 示例

```bash
python example/__main__.py
```

示例会在临时目录创建任务、规则、技能和一个假的 `claude` 命令，用于验证 `ai-servant` 的配置读取、Markdown 拼接、模型参数传递和标准输入转发。

Windows 可以运行：

```bat
example.bat
```

## 发布

```bash
./tools/pack.sh
```

Windows 可以运行：

```bat
tools\pack.bat
```

打包产物位于 `dist/`：单文件可执行体 `ai-servant` / `ai-servant.exe`，以及随包文档压缩包 `ai-servant-<version>-<platform>.tar.gz` / `.zip`。推送到 `main` 后，Release workflow 会用打包后的可执行文件运行完整示例，成功后覆盖 `v<version>` Release 附件。

## 异常情形

| 情形 | 处理 |
| --- | --- |
| config 无法读取或校验失败 | 打印错误到标准错误，返回 `1` |
| Markdown 文件不存在或无法按 UTF-8 读取 | 不启动 Claude CLI，返回 `1` |
| 本机找不到 `claude` 可执行文件 | 打印错误到标准错误，返回 `1` |
| Claude CLI 已启动并结束 | 透传 Claude CLI 的退出码 |
