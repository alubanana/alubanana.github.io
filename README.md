# Annan Chen / 陈安楠的个人网站

线上地址：https://alubanana.github.io/

项目、开发笔记与早期文章。当前网站使用Python和Markdown构建，由GitHub Actions部署到原GitHub Pages。

## 本地运行

```sh
python -m pip install -r requirements.txt
python build.py
python check_site.py
python -m http.server 8000 --directory dist
```

打开 http://localhost:8000 。日常改文章、项目和页面的入口见 [内容维护指南](CONTENT_GUIDE.md)。

## 内容

- `content/catalog.yml`：首页介绍、项目列表与外链。
- `content/pages/`：个人介绍。
- `content/projects/`：项目详情与有日期的项目回看。
- `content/notes/`：开发笔记。
- `_posts/`：2018—2020年原文章，保留原URL。
- `site_assets/`：当前布局样式及图片；`images/`保留原文章图表。
- `build.py`、`check_site.py`：构建与发布前检查。

`dist/`由构建生成。旧Jekyll布局和配置保留为历史源码，当前构建只读取上述内容入口。

本次英雄联盟文章增加2026年回看，原实验数字仍来自2020年团队报告。AI辅助代码开发和文字整理；项目事实与结果以相应原始资料为准。
