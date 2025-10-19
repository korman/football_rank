# 浩子足球数据统计系统

## 概述

一个用于统计和分析足球联赛数据的系统，使用SQLite作为数据库存储，支持多种排名算法包括Elo和OpenSkill。

## 技术栈

- Python
- SQLite (数据库)
- PyQt6 (GUI界面)
- pandas (数据处理)
- openskill (排名算法)

## 功能特点

- 支持从文件导入比赛数据到SQLite数据库
- 实现多种排名算法 (Elo, OpenSkill)
- 按联赛筛选和查看队伍排名
- 可视化展示排名数据和比赛统计

## 数据库

系统使用SQLite数据库存储比赛数据，数据库文件位于项目根目录的`match_data.db`。