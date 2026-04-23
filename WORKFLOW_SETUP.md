# GitHub Actions 工作流设置指南

由于 GitHub 权限限制，工作流文件需要通过 GitHub Web 界面创建。请按照以下步骤操作：

## 步骤 1：访问 GitHub Actions

1. 进入仓库：https://github.com/cxddgtb/mira
2. 点击 **Actions** 标签页
3. 点击 **New workflow**

## 步骤 2：创建工作流文件

1. 点击 **set up a workflow yourself**
2. 将文件名改为 `merge-interfaces.yml`
3. 复制以下内容到编辑器：

```yaml
name: MiraPlay Interface Aggregator

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - 'scripts/**'

jobs:
  aggregate:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Run aggregation script
        run: python scripts/merge_interfaces_v2.py

      - name: Check generated files
        run: |
          echo "=== Generated files ==="
          ls -lh dist/
          echo ""
          echo "=== Config file ==="
          head -20 dist/index.config.js

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add dist/
          if git diff --cached --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: auto update interface config $(date -u +'%Y-%m-%d %H:%M:%S')"
            git push
          fi

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

## 步骤 3：提交工作流

1. 点击 **Commit changes...**
2. 输入提交信息：`ci: add MiraPlay aggregator workflow`
3. 点击 **Commit new file**

## 步骤 4：启用 GitHub Pages

1. 进入 **Settings** → **Pages**
2. 在 **Source** 下拉菜单中选择 **Deploy from a branch**
3. 选择分支为 **gh-pages**
4. 点击 **Save**

## 步骤 5：运行工作流

1. 进入 **Actions** 标签页
2. 选择 **MiraPlay Interface Aggregator** 工作流
3. 点击 **Run workflow** → **Run workflow**

## 步骤 6：获取订阅链接

工作流完成后，您的订阅链接为：

```
https://cxddgtb.github.io/mira/index.config.js.md5
```

## 在 MiraPlay 中添加订阅

1. 打开 MiraPlay 应用
2. 进入 **设置** → **订阅管理**
3. 点击 **添加订阅**
4. 粘贴上述链接
5. 等待加载完成

---

**需要帮助？** 查看 [README.md](README.md) 或 [QUICKSTART.md](QUICKSTART.md)
