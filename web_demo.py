#!/usr/bin/env python3
"""
智能商品推荐系统 - Web演示界面
使用Flask创建简单的Web界面
"""

try:
    from flask import Flask, render_template_string, request, jsonify

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from product_recommend_api import ProductRecommendationAPI, get_available_options
import json
import os
import base64

# HTML模板 — 现代化 UI 重构
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎁 智能购物助手</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root{
            /* 现代配色方案 */
            --primary: #2563eb;       /* 亮蓝主色 */
            --primary-dark: #1e40af;  /* 深蓝交互 */
            --primary-light: #eff6ff; /* 浅蓝背景 */
            --accent: #0b3d91;        /* 保持原有的品牌色用于强调 */

            --bg-page: #f3f4f6;       /* 页面背景灰 */
            --bg-card: #ffffff;       /* 卡片白 */

            --text-main: #1f2937;
            --text-sub: #6b7280;
            --border: #e5e7eb;

            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);

            --radius-md: 12px;
            --radius-lg: 16px;
        }

        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
            font-family: 'Noto Sans SC', "Segoe UI", Tahoma, sans-serif;
            background: var(--bg-page);
            color: var(--text-main);
        }

        /* 布局容器 */
        .page {
            display: flex;
            gap: 24px;
            padding: 24px;
            box-sizing: border-box;
            height: 100vh;
            max-width: 1600px;
            margin: 0 auto;
        }

        /* === 左侧侧边栏 === */
        .sidebar {
            width: 280px;
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-md);
            display: flex;
            flex-direction: column;
            gap: 20px;
            border: 1px solid var(--border);
            flex-shrink: 0;
        }

        .user-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }

        .avatar-container {
            position: relative;
            margin-bottom: 16px;
        }

        .avatar-img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid var(--primary-light);
            box-shadow: var(--shadow-sm);
        }

        .user-id-group {
            width: 100%;
            text-align: center;
        }

        .user-id-label {
            font-size: 12px;
            color: var(--text-sub);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
            display: block;
        }

        #user_id_input {
            width: 100%;
            padding: 8px;
            font-size: 18px;
            font-weight: 700;
            color: var(--primary-dark);
            text-align: center;
            border: 1px solid transparent;
            border-radius: 6px;
            background: transparent;
            transition: all 0.2s;
        }

        #user_id_input:hover, #user_id_input:focus {
            background: var(--primary-light);
            border-color: var(--primary);
            outline: none;
        }

        /* 智能提示区域 */
        .tips-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
            overflow: hidden;
        }

        .tips-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .tips-title::before {
            content: "💡";
        }

        .tips-box {
            background: linear-gradient(145deg, #f0f7ff 0%, #e0eaff 100%);
            border-radius: var(--radius-md);
            padding: 16px;
            font-size: 13px;
            line-height: 1.5;
            color: #374151;
            flex: 1;
            overflow-y: auto;
            border: 1px solid #dbeafe;
        }

        .tips-box ul {
            padding-left: 16px;
            margin: 0;
        }

        .tips-box li {
            margin-bottom: 8px;
        }

        /* === 右侧主区域 === */
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
            min-width: 0; /* 防止flex子元素溢出 */
        }

        /* 顶部控制栏 */
        .controls-card {
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            padding: 16px 24px;
            box-shadow: var(--shadow-md);
            display: flex;
            gap: 20px;
            align-items: center;
            border: 1px solid var(--border);
            position: relative;
            z-index: 100;
        }

        .control-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .control-group.fixed-width { flex: 0 0 160px; }
        .control-group.fixed-width-lg { flex: 0 0 200px; }
        .control-group.fluid { flex: 1; min-width: 200px; }

        .control-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-sub);
        }

        .input-styled {
            background: var(--bg-page);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            color: var(--text-main);
            transition: 0.2s;
            width: 100%;
            box-sizing: border-box;
        }

        .input-styled:focus {
            border-color: var(--primary);
            background: #fff;
            outline: none;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        /* 文本域预览模式 */
        .preview-box {
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--text-main);
        }

        .preview-box:hover {
            border-color: #cbd5e1;
        }

        /* 聊天内容区域 */
        .chat-container {
            flex: 1;
            background: var(--bg-card);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
            z-index: 1;
        }

        .chat-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--border);
            font-weight: 700;
            font-size: 16px;
            color: var(--accent);
            background: #fff;
            z-index: 10;
        }

        #chatArea {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
            background: #ffffff;
            scroll-behavior: smooth;
        }

        /* 消息气泡样式 */
        .msg-wrapper {
            display: flex;
            margin-bottom: 16px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .msg-wrapper.user {
            justify-content: flex-end;
        }

        .msg-wrapper.assistant {
            justify-content: flex-start;
        }

        .bubble {
            max-width: 75%;
            padding: 12px 18px;
            border-radius: 18px;
            font-size: 15px;
            line-height: 1.6;
            position: relative;
        }

        .user .bubble {
            background: var(--primary);
            color: white;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }

        .assistant .bubble {
            background: #f3f4f6;
            color: #1f2937;
            border-bottom-left-radius: 4px;
        }

        /* 推荐结果样式优化 */
        .assistant .bubble ul {
            padding-left: 20px;
            margin: 8px 0;
        }

        .assistant .bubble li {
            margin-bottom: 4px;
        }

        .assistant .bubble strong {
            color: var(--accent);
        }

        /* 底部输入框 */
        .input-area {
            padding: 16px 24px;
            background: #fff;
            border-top: 1px solid var(--border);
        }

        .composer {
            display: flex;
            gap: 12px;
            align-items: center;
            background: var(--bg-page);
            padding: 8px 8px 8px 20px;
            border-radius: 30px;
            border: 1px solid transparent;
            transition: all 0.3s;
        }

        .composer:focus-within {
            background: #fff;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        }

        .composer-input {
            flex: 1;
            border: none;
            background: transparent;
            font-size: 15px;
            outline: none;
            color: var(--text-main);
        }

        .send-btn {
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: var(--primary);
            color: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background 0.2s;
            font-size: 18px;
        }

        .send-btn:hover {
            background: var(--primary-dark);
            transform: scale(1.05);
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        /* === 浮动聊天机器人 (Chatbot A/B) === */
        #floating-chats {
            position: fixed;
            bottom: 30px;
            left: 30px; /* 保持原逻辑在左侧，虽然通常在右侧，但这里遵循原设计 */
            z-index: 9999;
            display: flex;
            flex-direction: column-reverse; /* 让A在B下面，或者根据原逻辑调整 */
            gap: 16px;
            pointer-events: none; /* 让容器不遮挡点击，只让子元素响应 */
        }

        .floating-bubble {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            cursor: pointer;
            font-weight: 800;
            font-size: 20px;
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            pointer-events: auto;
            position: relative; /* 相对定位，移除原本的 fixed absolute */
            left: auto; bottom: auto; /* 重置原本的样式 */
        }

        .floating-bubble:hover {
            transform: scale(1.1) translateY(-4px);
        }

        /* 不同的机器人使用不同颜色 */
        #bubbleA {
            background: linear-gradient(135deg, #6366f1, #4f46e5); /* Indigo */
        }

        #bubbleB {
            background: linear-gradient(135deg, #ec4899, #db2777); /* Pink */
        }

        .floating-panel {
            position: fixed;
            left: 100px;
            bottom: 30px;
            width: 380px;
            height: 600px;
            max-height: 80vh;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
            display: none;
            z-index: 10000;
            overflow: hidden;
            flex-direction: column;
            pointer-events: auto;
            animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .floating-panel header {
            height: 50px;
            padding: 0 16px;
            background: var(--text-main);
            color: #fff;
            font-weight: 600;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .floating-panel .close-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            color: #fff;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .floating-panel .close-btn:hover {
            background: rgba(255,255,255,0.3);
        }

        /* 响应式调整 */
        @media (max-width: 900px) {
            .page { flex-direction: column; padding: 12px; height: auto; min-height: 100vh;}
            .sidebar { width: 100%; flex-direction: row; align-items: flex-start; }
            .user-card { flex-direction: row; border-bottom: none; border-right: 1px solid var(--border); padding-right: 20px; padding-bottom: 0; gap: 16px;}
            .avatar-container { margin-bottom: 0; }
            .tips-container { display: none; } /* 移动端隐藏提示以节省空间 */
            .controls-card { flex-wrap: wrap; }
            .control-group { flex: 1 1 140px; }
            .chat-container { height: 60vh; }
            #floating-chats { left: 16px; bottom: 16px; }
            .floating-panel { left: 16px; right: 16px; width: auto; bottom: 80px; }
        }
    </style>
</head>
<body>
    <div class="page">
        <aside class="sidebar" aria-label="侧边栏">
            <div class="user-card">
                <div class="avatar-container">
                    <img id="avatarImg" class="avatar-img" src="{{ url_for('static', filename='avatar.png') }}" 
                         alt="用户头像" 
                         title="点击更换"
                         onerror="this.onerror=null;this.src='data:image/svg+xml;utf8,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2780%27 height=%2780%27%3E%3Crect fill=%27%23e0e7ff%27 width=%27100%25%27 height=%27100%25%27 rx=%2740%27/%3E%3Ctext x=%2750%25%27 y=%2750%25%27 font-size=%2724%27 fill=%27%234f46e5%27 text-anchor=%27middle%27 dominant-baseline=%27central%27%3EUser%3C/text%3E%3C/svg%3E';">
                </div>
                <div class="user-id-group">
                    <label class="user-id-label">Current User ID</label>
                    <input id="user_id_input" type="number" value="25" min="1">
                </div>
            </div>

            <div class="tips-container">
                <div class="tips-title">购物分析 & 建议</div>
                <div id="tipsBox" class="tips-box">
                    <div style="display:flex;justify-content:center;align-items:center;height:100%;color:#9ca3af;">
                        正在分析用户画像...
                    </div>
                </div>
            </div>
        </aside>

        <main class="main" role="main">
            <div class="controls-card">
                <div class="control-group fixed-width">
                    <label class="control-label">预算 (¥)</label>
                    <input id="budget" type="number" step="100" class="input-styled" placeholder="不限">
                </div>
                <div class="control-group fixed-width-lg">
                    <label class="control-label">送礼对象</label>
                    <select id="recipient" name="recipient" class="input-styled">
                        {% for key, value in gift_recipients_dict.items() %}
                        <option value="{{ key }}">{{ key }} ({{ value }})</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="control-group fluid">
                    <label class="control-label">对象详细画像</label>
                    <div style="position:relative; z-index:1000; min-height:42px;">
                        <div id="recipient_preview" class="input-styled preview-box" title="点击编辑详细信息" style="position:relative;">
                            年龄、爱好等（选填）
                        </div>
                        <textarea id="recipient_info" class="input-styled hidden-edit" 
                                  placeholder="例如：25岁，喜欢摄影和户外运动" 
                                  style="display:none; height:80px; position:absolute; top:0; left:0; right:0; z-index:1001; resize:vertical; background:#fff; box-shadow: 0 4px 12px rgba(0,0,0,0.15);"></textarea>
                    </div>
                </div>
            </div>

            <div class="chat-container">
                <div class="chat-header">
                    AI 导购助手
                </div>

                <div id="chatArea" aria-label="对话历史">
                    <div class="msg-wrapper assistant">
                        <div class="bubble">
                            你好！我是你的智能购物助手。使用方法如下：<br>
                            1. AI 导购助手：输入需求并完善补充信息，即可智能推荐商品；<br>
                            2. 智能售后客服：输入问题，即可智能解答；<br>
                            3. 商品比价工具：输入商品名称，即可比价。<br>
                            左侧根据您的购物习惯，为您贴心提示~
                        </div>
                    </div>
                </div>

                <div class="input-area">
                    <div class="composer">
                        <input id="requirement" name="requirement" class="composer-input" 
                               placeholder="在此输入需求（例如：想要一个新年礼物）..." autocomplete="off">
                        <button id="submitBtn" class="send-btn" title="发送 (Enter)">
                            <span style="margin-left:2px;">&#10148;</span>
                        </button>
                    </div>
                </div>
            </div>
        </main>

        <div id="floating-chats">
            <div id="bubbleA" class="floating-bubble" data-index="A" title="打开 商品比价工具">比价</div>
            <div id="bubbleB" class="floating-bubble" data-index="B" title="打开 智能售后客服">售后</div>
        </div>

        <div id="panelA" class="floating-panel" aria-hidden="true">
            <iframe id="iframeA" data-src="https://udify.app/chatbot/45aotSLawwRE4ZPc" src="about:blank" title="商品比价工具" style="width:100%;height:100%;border:0;"></iframe>
        </div>
        <div id="panelB" class="floating-panel" aria-hidden="true">
            <iframe id="iframeB" data-src="https://udify.app/chatbot/eMVd9BiHBSLBiIR7" src="about:blank" title="智能售后客服" style="width:100%;height:100%;border:0;"></iframe>
        </div>

    </div>

    <script>
        // 消息气泡生成器
        function addUserMessage(text){
            const chat = document.getElementById('chatArea');
            const wrapper = document.createElement('div');
            wrapper.className = 'msg-wrapper user';

            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerText = text;

            wrapper.appendChild(bubble);
            chat.appendChild(wrapper);
            chat.scrollTop = chat.scrollHeight;
        }

        function addAssistantMessage(htmlContent){
            const chat = document.getElementById('chatArea');
            const wrapper = document.createElement('div');
            wrapper.className = 'msg-wrapper assistant';

            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = htmlContent;

            wrapper.appendChild(bubble);
            chat.appendChild(wrapper);
            chat.scrollTop = chat.scrollHeight;
        }

        // 切换 recipient 时是否需要 recipient_info
        const recipientSelect = document.getElementById('recipient');
        const recipientInfoInput = document.getElementById('recipient_info');
        const preview = document.getElementById('recipient_preview');

        if(recipientSelect){
            recipientSelect.addEventListener('change', function(){
                const defaultText = this.value === '自己' ? '送给自己可不填写' : '请提供详细信息（年龄、爱好、职业等）';
                recipientInfoInput.placeholder = defaultText;

                if(!recipientInfoInput.value || recipientInfoInput.value.trim()===''){
                    preview.textContent = defaultText;
                    preview.title = defaultText;
                }
            });
        }

        // recipient_info preview & expand behavior
        (function(){
            if(!preview || !recipientInfoInput) return;

            // Initialize
            const initText = recipientInfoInput.value || recipientInfoInput.placeholder || '年龄、爱好等（选填）';
            preview.textContent = initText.length > 20 ? initText.slice(0,20) + '...' : initText;

            preview.addEventListener('click', function(){
                preview.style.visibility = 'hidden';
                recipientInfoInput.style.display = 'block';
                recipientInfoInput.focus();
            });

            recipientInfoInput.addEventListener('blur', function(){
                const full = recipientInfoInput.value || recipientInfoInput.placeholder || '';
                preview.textContent = full.length > 20 ? full.slice(0,20) + '...' : full;
                preview.title = full;
                recipientInfoInput.style.display = 'none';
                preview.style.visibility = 'visible';
            });
        })();

        // Send Logic
        async function sendRequirement(){
            const requirementInput = document.getElementById('requirement');
            const requirement = requirementInput.value.trim();
            const budget = document.getElementById('budget').value || '';
            const recipient = document.getElementById('recipient').value || '自己';
            const recipient_info = document.getElementById('recipient_info').value || '';
            const userId = parseInt(document.getElementById('user_id_input').value) || 25;

            if(!requirement) return;

            // UI Feedback
            addUserMessage(requirement);
            requirementInput.value = '';

            // Loading indicator could be added here
            const loadingWrapper = document.createElement('div');
            loadingWrapper.id = 'loading-msg';
            loadingWrapper.className = 'msg-wrapper assistant';
            loadingWrapper.innerHTML = '<div class="bubble" style="color:#6b7280;">正在思考推荐方案...</div>';
            document.getElementById('chatArea').appendChild(loadingWrapper);
            document.getElementById('chatArea').scrollTop = document.getElementById('chatArea').scrollHeight;

            const payload = {
                user_id: userId,
                budget: budget,
                recipient: recipient,
                recipient_info: recipient_info,
                requirement: requirement
            };

            try{
                const resp = await fetch('/recommend', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify(payload)
                });
                const result = await resp.json();

                // Remove loading
                const loader = document.getElementById('loading-msg');
                if(loader) loader.remove();

                if(result.success){
                    let html = '<div style="font-size:16px;font-weight:700;margin-bottom:8px;color:#0b3d91;">🎁 推荐结果</div>';
                    if(result.analysis){
                        html += `<div style="margin-bottom:8px;color:#4b5563;">${result.analysis}</div>`;
                    }
                    if(result.recommendations && result.recommendations.length){
                        html += '<div style="margin-bottom:8px;"><ul>';
                        result.recommendations.forEach(rec=>{
                            html += `<li style="margin-bottom:8px;">
                                <span style="font-weight:600;color:#111;">${rec.category}</span> 
                                <span style="color:#2563eb;font-size:0.9em;background:#eff6ff;padding:2px 6px;border-radius:4px;">${rec.price_range}</span>
                                <div style="margin-top:2px;color:#374151;">${rec.products.join('、')}</div>
                            </li>`;
                        });
                        html += '</ul></div>';
                    }
                    if(result.buying_tips && result.buying_tips.length){
                        html += `<div style="margin-top:8px;padding-top:8px;border-top:1px dashed #e5e7eb;"><strong>💡 购买建议：</strong><ul style="color:#4b5563;">${result.buying_tips.map(t=>`<li>${t}</li>`).join('')}</ul></div>`;
                    }
                    addAssistantMessage(html);
                    updateTipsFromResult(result);
                } else {
                    addAssistantMessage('<div style="color:#dc2626"><strong>❌ 推荐失败：</strong>' + (result.error || '未知错误') + '</div>');
                }

            }catch(e){
                console.error(e);
                const loader = document.getElementById('loading-msg');
                if(loader) loader.remove();
                addAssistantMessage('<div style="color:#dc2626"><strong>❌ 请求失败：</strong>' + e.message + '</div>');
            }
        }

        document.getElementById('submitBtn').addEventListener('click', sendRequirement);
        document.getElementById('requirement').addEventListener('keydown', function(e){
            if(e.key === 'Enter' && !e.shiftKey){
                e.preventDefault();
                sendRequirement();
            }
        });
    </script>

    <script>
        function closeAllPanels(){
            ['A','B'].forEach(id=>{
                const panel = document.getElementById('panel'+id);
                if(panel) panel.style.display = 'none';
            });
        }
        function togglePanel(id){
            const panel = document.getElementById('panel'+id);
            const iframe = document.getElementById('iframe'+id);
            if(!panel) return;
            const isOpen = panel.style.display === 'flex'; // Changed from block to flex for CSS layout

            // close others
            closeAllPanels();

            if(!isOpen){
                if(iframe && (!iframe.src || iframe.src === 'about:blank')){
                    iframe.src = iframe.dataset.src;
                }
                panel.style.display = 'flex';
            } else {
                panel.style.display = 'none';
            }
        }

        document.getElementById('bubbleA').addEventListener('click', ()=> togglePanel('A'));
        document.getElementById('bubbleB').addEventListener('click', ()=> togglePanel('B'));
    </script>

    <script>
        // Fetch smart suggestions
        async function fetchSmartSuggestions(userId){
            const tipsBox = document.getElementById('tipsBox');
            if(!tipsBox) return;
            tipsBox.innerHTML = '<div style="color:#9ca3af;text-align:center;">正在分析购买习惯...</div>';
            try{
                const resp = await fetch(`/smart_suggestions?user_id=${encodeURIComponent(userId)}`);
                const result = await resp.json();
                if(result.success){
                    const suggestions = result.suggestions || [];
                    if(suggestions.length === 0){
                        tipsBox.innerHTML = '<div>暂无基于购买记录的推荐。</div>';
                        return;
                    }
                    let html = '<ul>';
                    suggestions.forEach(s=>{
                        html += `<li><strong style="color:#1f2937;">${s.title}</strong><div style="margin-top:2px;">${s.message}</div></li>`;
                    });
                    html += '</ul>';
                    tipsBox.innerHTML = html;
                } else {
                    tipsBox.innerHTML = `<div style="color:#dc2626;">获取推荐失败</div>`;
                }
            }catch(e){
                tipsBox.innerHTML = `<div style="color:#dc2626;">网络请求失败</div>`;
            }
        }

        const userIdInput = document.getElementById('user_id_input');
        if(userIdInput){
            userIdInput.addEventListener('change', ()=> {
                const uid = parseInt(userIdInput.value) || 0;
                if(uid>0) fetchSmartSuggestions(uid);
            });
            fetchSmartSuggestions(parseInt(userIdInput.value) || 25);
        }

        function updateTipsFromResult(result){
            const tipsBox = document.getElementById('tipsBox');
            if(!tipsBox) return;
            if(result.buying_tips && result.buying_tips.length){
                let html = '<ul>';
                result.buying_tips.forEach(t => html += `<li>${t}</li>`);
                html += '</ul>';
                tipsBox.innerHTML = html;
            }
        }
    </script>
</body>
</html>
"""


def create_app():
    """创建Flask应用"""
    if not FLASK_AVAILABLE:
        print("❌ Flask未安装，无法启动Web界面")
        print("安装方法: pip3 install flask")
        return None

    app = Flask(__name__)
    api = ProductRecommendationAPI()

    @app.route('/')
    def index():
        """主页"""
        options = get_available_options()
        user_summary = api.get_user_summary(25)

        # 确保生成默认头像
        static_dir = os.path.join(app.root_path, 'static')
        static_avatar = os.path.join(static_dir, 'avatar.png')
        try:
            if not os.path.exists(static_avatar):
                os.makedirs(static_dir, exist_ok=True)
                # 简单的 1x1 像素占位符，实际会由前端 SVG 覆盖
                placeholder_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
                with open(static_avatar, 'wb') as f:
                    f.write(base64.b64decode(placeholder_png_b64))
        except Exception as e:
            pass

        return render_template_string(HTML_TEMPLATE,
                                      gift_recipients=list(options['gift_recipients'].keys()),
                                      gift_recipients_dict=options['gift_recipients'],
                                      category_count=len(options['product_categories']),
                                      price_min=f"{options['price_range']['min']:.2f}",
                                      price_max=f"{options['price_range']['max']:.2f}",
                                      avg_spending=f"{user_summary.get('avg_order_amount', 0):.2f}"
                                      )

    @app.route('/recommend', methods=['POST'])
    def recommend():
        """处理推荐请求"""
        try:
            data = request.json

            # 转换数据类型
            user_id = int(data['user_id'])
            budget = float(data['budget']) if data.get('budget') else None
            recipient = data['recipient']
            recipient_info = data.get('recipient_info', '')
            requirement = data['requirement']

            # 使用默认API实例（已包含API密钥）
            result = api.get_product_recommendations(
                user_id=user_id,
                budget=budget,
                recipient=recipient,
                recipient_info=recipient_info,
                requirement=requirement
            )

            return jsonify(result)

        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"处理请求时出错: {str(e)}"
            })

    @app.route('/smart_suggestions')
    def smart_suggestions():
        """返回基于用户购买记录的智能建议（用于左侧 tips 显示）"""
        try:
            user_id = int(request.args.get('user_id', 0))
            if user_id <= 0:
                return jsonify({"success": False, "error": "无效的 user_id"})
            suggestions = api.get_smart_suggestions(user_id)
            return jsonify(suggestions)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return app


def main():
    """主函数"""
    print("🎁 智能商品推荐系统 (美化版)")
    print("=" * 50)

    if not FLASK_AVAILABLE:
        print("❌ Flask未安装，无法启动Web界面")
        return

    app = create_app()
    if app:
        print("🌐 启动Web界面...")
        print("📱 访问地址: http://localhost:5000")
        try:
            app.run(debug=True, host='0.0.0.0', port=5000)
        except KeyboardInterrupt:
            print("\n👋 服务已停止")


if __name__ == "__main__":
    main()