# 内容维护

网站地址：https://alubanana.github.io/

## 改哪里

| 内容 | 文件 |
|---|---|
| 首页介绍、项目列表、外链 | `content/catalog.yml` |
| 关于我 | `content/pages/about.md` |
| 单条教育、工作、实习时间线 | `content/timeline.yml`；`journey.yml`保留旧版数据 |
| 近期项目详情、英雄联盟回看 | `content/projects/*.md` |
| 开发笔记 | `content/notes/*.md` |
| 2018—2020 原文章 | `_posts/YYYY-MM-DD-*.md` |
| 英文介绍、笔记与近期项目 | `content/en/*.md` |
| 七篇旧文完整中文翻译 | `content/translations/zh/*.md` |
| 布局与构建 | `build.py` |
| 字体、配色与响应式布局 | `site_assets/studio.css` |
| 语言偏好、搜索与筛选 | `site_assets/site.js` |
| 统计接收地址与启用状态 | `content/analytics.json` |
| 图片 | `site_assets/`；早期文章继续使用 `images/` |

`dist/`是构建结果，不手工修改。旧Jekyll主题文件保留作历史源码；当前网站由`build.py`和GitHub Actions构建。

## 预览和发布

Python 3.10及以上：

```sh
python -m pip install -r requirements.txt
python build.py
python check_site.py
python -m http.server 8000 --directory dist
```

打开 http://localhost:8000 。检查桌面、390px窄屏、文章图表与跳转后，提交并推送到`main`。Website工作流会构建、检查站内链接和资源，再部署到原GitHub Pages。

## 新增笔记

在`content/notes/`添加Markdown文件，填写：

```yaml
---
title: 文章标题
description: 一句话说明这篇文章的内容。
date: 2026-10-27
path: /notes/article-slug/
kind: 开发笔记
---
```

正文从标题以下开始；构建时自动加入笔记列表、站点地图和RSS。

同时在`content/en/`添加同名英文Markdown。中文页面保留原地址，英文版使用`/en/`前缀；右上角语言入口保持同一篇文章，手动选择保存在浏览器。首次访问首页按浏览器语言选择，深层链接使用URL指定语言。

## 刷新旧项目

1. 核对原文章、报告和代码，登记实际读过的版本。
2. 修正失效资源或明显错链；保留原文章地址和项目日期。
3. 大幅重写时，另写有回看日期的新页面，并从原文链接过去。历史实验结果注明出处；新实验单独记录数据、代码、切分和结果。
4. 项目贡献按实际团队记录描述。改进方案与已完成的实验分别写清。

七篇旧文均有完整中文译文和英文原文，顶部有2026年阅读导引与流程图。修改原文后应同步对应译文；链接、图表、代码与数字由构建检查核对。英雄联盟另有`/projects/league-of-legends/`回看页，历史模型没有重新训练。

项目库标题、摘要和筛选类别来自`catalog.yml`与`build.py`中的英文映射；时间线中的比赛标签集中在`build.py`的`timeline()`。

## 访问统计

统计后端在网站仓库外的独立`analytics-service/`项目，不把后台访问配置或访客记录放进GitHub。统计开关由`content/analytics.json`控制；只有完成具体字段与目的地授权、后台验证后才开启。关闭时不加载采集脚本。

## 两项独立工具

本仓库维护网站介绍；工具实现分别在`tech-research-dashboard`和`ai-context-memory`。公开演示的数据日期、版本、截图和链接需要与相应仓库核对后一起更新。

## 回退

保留已发布提交，使用新的revert提交回退，再运行Website工作流。不要改写已公开的版本标签。发布状态可在GitHub Actions的Website和Settings → Pages查看。
