# ai-servant

本地 AI 助手工具；当前为项目骨架，后续扩展 CLI 子命令与业务能力。

## 项目结构

```
ai_servant/
├── src/              # 源码与 CLI 入口
├── tests/            # 单元测试
├── update.bat        # Windows：创建 venv 并安装依赖
├── update.sh         # POSIX：同上
├── test.bat          # Windows：运行测试
└── test.sh           # POSIX：运行测试
```

## 命令行参数

`python src`

| 长参数 | 短参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- | --- |
| --version | -v | | | | 显示版本号 |
