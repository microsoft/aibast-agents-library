#!/usr/bin/env python3
"""
M365 Demo Updater Agent
Updates all demo HTML files to use the M365 Copilot style pattern
"""

import os
import json
import glob
from pathlib import Path
from typing import Dict, List, Any

class M365DemoUpdaterAgent:
    """Agent that updates demo files to M365 Copilot pattern"""
    
    def __init__(self):
        self.name = "M365 Demo Updater"
        self.description = "Updates all demo HTML files to use the M365 Copilot style pattern"
        self.updated_files = []
        self.failed_files = []
        
    def get_m365_template(self, agent_name: str, agent_icon: str, agent_color: str, 
                          demo_script: str, welcome_cards: str, search_placeholder: str = "Search") -> str:
        """Generate M365 Copilot HTML template with agent-specific customization"""
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M365 Copilot - {agent_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            background: #faf9f8;
            height: 100vh;
            display: flex;
            overflow: hidden;
            color: #323130;
        }}

        /* Sidebar */
        .sidebar {{
            width: 260px;
            background: #ffffff;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #edebe9;
        }}

        /* Sidebar Header */
        .sidebar-header {{
            padding: 12px 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #edebe9;
            height: 48px;
        }}

        .copilot-icon {{
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, #b4a0ff 0%, #ff7eb9 50%, #7ee7fc 100%);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}

        .copilot-icon::before {{
            content: '';
            position: absolute;
            width: 12px;
            height: 12px;
            background: white;
            border-radius: 2px;
            opacity: 0.9;
        }}

        .sidebar-title {{
            font-size: 14px;
            font-weight: 600;
            color: #323130;
        }}

        .sidebar-button {{
            margin-left: auto;
            background: none;
            border: none;
            padding: 4px;
            cursor: pointer;
            color: #605e5c;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            width: 32px;
            height: 32px;
        }}

        .sidebar-button:hover {{
            background: #f3f2f1;
        }}

        /* Search Box */
        .search-container {{
            padding: 8px 16px;
            border-bottom: 1px solid #edebe9;
        }}

        .search-box {{
            position: relative;
            width: 100%;
        }}

        .search-icon {{
            position: absolute;
            left: 8px;
            top: 50%;
            transform: translateY(-50%);
            color: #605e5c;
            font-size: 14px;
        }}

        .search-input {{
            width: 100%;
            padding: 6px 8px 6px 32px;
            border: 1px solid #d2d0ce;
            border-radius: 4px;
            font-size: 14px;
            background: #faf9f8;
            outline: none;
            transition: all 0.2s;
        }}

        .search-input:focus {{
            border-color: #605e5c;
            background: #ffffff;
        }}

        /* Navigation */
        .nav-section {{
            flex: 1;
            overflow-y: auto;
            padding: 4px 0;
        }}

        .nav-item {{
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            font-size: 14px;
            color: #323130;
            transition: background 0.1s;
            position: relative;
            user-select: none;
        }}

        .nav-item:hover {{
            background: #f3f2f1;
        }}

        .nav-item.active {{
            background: #f3f2f1;
        }}

        .nav-item.active::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 8px;
            bottom: 8px;
            width: 2px;
            background: {agent_color};
            border-radius: 1px;
        }}

        .nav-icon {{
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        /* Demo Controls Section */
        .demo-controls-section {{
            border-top: 1px solid #edebe9;
            padding: 12px 16px;
            background: #faf9f8;
        }}

        .demo-controls-title {{
            font-size: 12px;
            font-weight: 600;
            color: #605e5c;
            margin-bottom: 8px;
        }}

        .demo-controls {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}

        .demo-btn {{
            padding: 6px 12px;
            border: 1px solid #d2d0ce;
            border-radius: 4px;
            background: white;
            font-size: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            color: #323130;
            transition: all 0.2s;
        }}

        .demo-btn:hover:not(:disabled) {{
            background: #f3f2f1;
            border-color: #605e5c;
        }}

        .demo-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        .demo-btn.primary {{
            background: {agent_color};
            color: white;
            border-color: {agent_color};
        }}

        .demo-btn.primary:hover:not(:disabled) {{
            filter: brightness(0.9);
        }}

        /* Bottom section */
        .sidebar-bottom {{
            border-top: 1px solid #edebe9;
            padding: 8px 0;
        }}

        .user-section {{
            padding: 8px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: background 0.1s;
        }}

        .user-section:hover {{
            background: #f3f2f1;
        }}

        .user-avatar {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: {agent_color};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }}

        /* Main Content */
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #faf9f8;
        }}

        /* Header */
        .content-header {{
            height: 48px;
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #ffffff;
            border-bottom: 1px solid #edebe9;
        }}

        .header-title {{
            font-size: 14px;
            color: #605e5c;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: #f3f2f1;
            border-radius: 4px;
            font-size: 12px;
            color: #605e5c;
        }}

        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
        }}

        .status-dot.processing {{
            background: #f59e0b;
            animation: pulse 1s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}

        /* Chat Container */
        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        /* Chat Messages */
        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: block;
        }}

        .message {{
            max-width: 900px;
            margin: 0 auto 24px;
        }}

        .message-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}

        .message-avatar-user {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: {agent_color};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
        }}

        .message-avatar-agent {{
            width: 28px;
            height: 28px;
            border-radius: 6px;
            background: linear-gradient(135deg, {agent_color} 0%, #40e0d0 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
        }}

        .message-author {{
            font-size: 14px;
            font-weight: 600;
            color: #323130;
        }}

        .message-tag {{
            padding: 2px 8px;
            background: #f3f2f1;
            border-radius: 4px;
            font-size: 12px;
            color: #605e5c;
        }}

        .message-time {{
            font-size: 12px;
            color: #a19f9d;
        }}

        .message-content {{
            margin-left: 40px;
            font-size: 14px;
            line-height: 1.6;
            color: #323130;
        }}

        /* Agent Cards */
        .agent-card {{
            margin-left: 40px;
            margin-top: 16px;
            background: white;
            border: 1px solid #edebe9;
            border-radius: 8px;
            overflow: hidden;
        }}

        .agent-card-header {{
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid #edebe9;
            background: linear-gradient(135deg, rgba(0, 120, 212, 0.05) 0%, rgba(64, 224, 208, 0.05) 100%);
        }}

        .agent-card-icon {{
            font-size: 20px;
        }}

        .agent-card-title {{
            font-size: 16px;
            font-weight: 600;
            color: #323130;
        }}

        .agent-card-status {{
            margin-left: auto;
            padding: 4px 12px;
            background: #10b981;
            color: white;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        .agent-card-content {{
            padding: 16px;
        }}

        .detail-list {{
            list-style: none;
        }}

        .detail-item {{
            padding: 8px 0;
            font-size: 14px;
            color: #323130;
            display: flex;
            gap: 8px;
            border-bottom: 1px solid #f3f2f1;
        }}

        .detail-item:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            font-weight: 600;
            min-width: 180px;
            color: #605e5c;
        }}

        .detail-value {{
            color: #323130;
            flex: 1;
        }}

        /* Input Container */
        .input-container {{
            padding: 16px 20px;
            background: white;
            border-top: 1px solid #edebe9;
        }}

        .input-wrapper {{
            max-width: 900px;
            margin: 0 auto;
            position: relative;
        }}

        .input-field {{
            width: 100%;
            padding: 12px 48px 12px 16px;
            border: 1px solid #d2d0ce;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            resize: none;
            outline: none;
            background: #faf9f8;
            transition: all 0.2s;
            min-height: 44px;
            max-height: 120px;
        }}

        .input-field:focus {{
            border-color: {agent_color};
            background: white;
        }}

        .input-actions {{
            position: absolute;
            right: 8px;
            bottom: 8px;
            display: flex;
            gap: 4px;
        }}

        .input-button {{
            width: 28px;
            height: 28px;
            border: none;
            background: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            color: #605e5c;
            transition: all 0.1s;
        }}

        .input-button:hover {{
            background: #f3f2f1;
        }}

        .input-button.send {{
            color: {agent_color};
        }}

        .input-button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}

        /* Typing indicator */
        .typing-indicator {{
            margin-left: 40px;
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }}

        .typing-dot {{
            width: 8px;
            height: 8px;
            background: #605e5c;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }}

        .typing-dot:nth-child(2) {{
            animation-delay: 0.2s;
        }}

        .typing-dot:nth-child(3) {{
            animation-delay: 0.4s;
        }}

        @keyframes typing {{
            0%, 60%, 100% {{
                transform: translateY(0);
                opacity: 0.5;
            }}
            30% {{
                transform: translateY(-10px);
                opacity: 1;
            }}
        }}

        /* Welcome state - hidden when chat is active */
        .welcome-screen {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }}

        .welcome-screen.hidden {{
            display: none;
        }}

        .welcome-title {{
            font-size: 36px;
            font-weight: 600;
            color: #323130;
            margin-bottom: 16px;
            text-align: center;
        }}

        .welcome-subtitle {{
            font-size: 16px;
            color: #605e5c;
            margin-bottom: 48px;
            text-align: center;
        }}

        .suggestion-cards {{
            display: flex;
            gap: 20px;
            width: 100%;
            max-width: 900px;
        }}

        .suggestion-card {{
            flex: 1;
            background: white;
            border: 1px solid #edebe9;
            border-radius: 8px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s;
            min-height: 120px;
        }}

        .suggestion-card:hover {{
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
            border-color: {agent_color};
        }}

        .card-icon {{
            font-size: 24px;
            margin-bottom: 12px;
        }}

        .card-title {{
            font-size: 14px;
            font-weight: 600;
            color: #323130;
            margin-bottom: 8px;
        }}

        .card-description {{
            font-size: 13px;
            color: #605e5c;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <!-- Sidebar -->
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="copilot-icon"></div>
            <span class="sidebar-title">M365 Copilot</span>
            <button class="sidebar-button">☰</button>
        </div>

        <div class="search-container">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" class="search-input" placeholder="{search_placeholder}">
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-item active">
                <div class="nav-icon">💬</div>
                <span>Chat</span>
            </div>
            <div class="nav-item">
                <div class="nav-icon">🤖</div>
                <span>Agents</span>
            </div>
            <div class="nav-item">
                <div class="nav-icon">💬</div>
                <span>Conversations</span>
            </div>
            <div class="nav-item">
                <div class="nav-icon">📄</div>
                <span>Pages</span>
            </div>
            <div class="nav-item">
                <div class="nav-icon">➕</div>
                <span>Create</span>
            </div>
            <div class="nav-item">
                <div class="nav-icon">📱</div>
                <span>Apps</span>
            </div>
            <div class="nav-item">
                <div class="nav-icon">⚙️</div>
                <span>Admin</span>
            </div>
        </div>

        <!-- Demo Controls -->
        <div class="demo-controls-section">
            <div class="demo-controls-title">Demo Controls</div>
            <div class="demo-controls">
                <button class="demo-btn primary" onclick="startDemo()" id="startBtn">
                    ▶️ Start
                </button>
                <button class="demo-btn" onclick="pauseDemo()" id="pauseBtn" disabled>
                    ⏸️ Pause
                </button>
                <button class="demo-btn" onclick="resetDemo()" id="resetBtn">
                    🔄 Reset
                </button>
                <button class="demo-btn" onclick="skipToNext()" id="skipBtn" disabled>
                    ⏭️ Skip
                </button>
            </div>
        </div>

        <div class="sidebar-bottom">
            <div class="user-section">
                <div class="user-avatar">KA</div>
                <span style="font-size: 14px;">Demo User</span>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
        <div class="content-header">
            <div class="header-title">{agent_name} Agent</div>
            <div class="header-actions">
                <div class="status-indicator">
                    <span class="status-dot" id="statusDot"></span>
                    <span id="statusText">Ready</span>
                </div>
            </div>
        </div>

        <div class="chat-container">
            <!-- Welcome Screen -->
            <div class="welcome-screen" id="welcomeScreen">
                <h1 class="welcome-title">{agent_icon} {agent_name}</h1>
                <p class="welcome-subtitle">Agent-powered automation and intelligence</p>
                
                <div class="suggestion-cards">
                    {welcome_cards}
                </div>
            </div>

            <!-- Chat Messages -->
            <div class="chat-messages" id="chatMessages" style="display: none;">
                <!-- Messages will be dynamically added here -->
            </div>

            <!-- Input Container -->
            <div class="input-container">
                <div class="input-wrapper">
                    <textarea 
                        class="input-field" 
                        id="messageInput" 
                        placeholder="Type your message..."
                        rows="1"
                        onkeypress="handleKeyPress(event)"
                        oninput="autoResize(this)"
                    ></textarea>
                    <div class="input-actions">
                        <button class="input-button">📎</button>
                        <button class="input-button send" onclick="sendCurrentMessage()" id="sendButton">
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // State
        let demoState = {{
            isPlaying: false,
            isPaused: false,
            currentStep: 0,
            messageTimer: null,
            typingTimer: null
        }};

        // Demo script
        const demoScript = {demo_script};

        let currentMessageIndex = 0;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('{agent_name} Agent initialized');
        }});

        // Auto resize textarea
        function autoResize(textarea) {{
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        }}

        // Handle key press
        function handleKeyPress(event) {{
            if (event.key === 'Enter' && !event.shiftKey) {{
                event.preventDefault();
                sendCurrentMessage();
            }}
        }}

        // Send current message
        function sendCurrentMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (message) {{
                // Hide welcome screen and show chat
                document.getElementById('welcomeScreen').classList.add('hidden');
                document.getElementById('chatMessages').style.display = 'block';
                
                // Add user message
                addMessage('user', message);
                
                input.value = '';
                autoResize(input);
                
                // Simulate agent response
                setTimeout(() => {{
                    showTypingIndicator();
                    setTimeout(() => {{
                        hideTypingIndicator();
                        addMessage('agent', 'Processing your request. Please use the demo controls to see a full demonstration.');
                    }}, 1500);
                }}, 500);
            }}
        }}

        // Demo controls
        function startDemo() {{
            if (demoState.isPlaying && !demoState.isPaused) return;
            
            demoState.isPlaying = true;
            demoState.isPaused = false;
            
            document.getElementById('startBtn').disabled = true;
            document.getElementById('pauseBtn').disabled = false;
            document.getElementById('skipBtn').disabled = false;
            
            updateStatus('processing', 'Running Demo...');
            
            // Hide welcome and show chat
            document.getElementById('welcomeScreen').classList.add('hidden');
            document.getElementById('chatMessages').style.display = 'block';
            
            if (currentMessageIndex === 0) {{
                document.getElementById('chatMessages').innerHTML = '';
            }}
            
            playNextMessage();
        }}

        function pauseDemo() {{
            demoState.isPaused = true;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            
            clearTimeout(demoState.messageTimer);
            clearTimeout(demoState.typingTimer);
            
            updateStatus('idle', 'Paused');
        }}

        function resetDemo() {{
            clearTimeout(demoState.messageTimer);
            clearTimeout(demoState.typingTimer);
            
            demoState.isPlaying = false;
            demoState.isPaused = false;
            currentMessageIndex = 0;
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('skipBtn').disabled = true;
            
            updateStatus('idle', 'Ready');
            
            // Show welcome screen
            document.getElementById('welcomeScreen').classList.remove('hidden');
            document.getElementById('chatMessages').style.display = 'none';
            document.getElementById('chatMessages').innerHTML = '';
        }}

        function skipToNext() {{
            clearTimeout(demoState.messageTimer);
            clearTimeout(demoState.typingTimer);
            hideTypingIndicator();
            
            if (currentMessageIndex < demoScript.length) {{
                const message = demoScript[currentMessageIndex];
                addDemoMessage(message);
                currentMessageIndex++;
                
                if (currentMessageIndex < demoScript.length) {{
                    demoState.messageTimer = setTimeout(() => {{
                        playNextMessage();
                    }}, 1000);
                }} else {{
                    completeDemo();
                }}
            }}
        }}

        function playNextMessage() {{
            if (!demoState.isPlaying || demoState.isPaused) return;
            
            if (currentMessageIndex >= demoScript.length) {{
                completeDemo();
                return;
            }}
            
            const message = demoScript[currentMessageIndex];
            
            if (message.type === 'agent') {{
                showTypingIndicator();
                demoState.typingTimer = setTimeout(() => {{
                    hideTypingIndicator();
                    addDemoMessage(message);
                    currentMessageIndex++;
                    
                    const delay = message.delay || 2000;
                    demoState.messageTimer = setTimeout(() => {{
                        playNextMessage();
                    }}, delay);
                }}, message.typingTime || 2000);
            }} else {{
                addDemoMessage(message);
                currentMessageIndex++;
                
                const delay = message.delay || 1500;
                demoState.messageTimer = setTimeout(() => {{
                    playNextMessage();
                }}, delay);
            }}
        }}

        function addDemoMessage(message) {{
            if (message.type === 'user') {{
                addMessage('user', message.content);
            }} else if (message.type === 'agent') {{
                addMessage('agent', message.content, message.agentData);
            }}
        }}

        function addMessage(type, content, agentData) {{
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const time = new Date().toLocaleString('en-US', {{ 
                hour: 'numeric', 
                minute: '2-digit'
            }});

            if (type === 'user') {{
                messageDiv.innerHTML = `
                    <div class="message-header">
                        <div class="message-avatar-user">U</div>
                        <span class="message-author">You</span>
                        <span class="message-time">${{time}}</span>
                    </div>
                    <div class="message-content">${{content}}</div>
                `;
            }} else {{
                let html = `
                    <div class="message-header">
                        <div class="message-avatar-agent">{agent_icon}</div>
                        <span class="message-author">{agent_name}</span>
                        <span class="message-tag">Agent</span>
                        <span class="message-time">${{time}}</span>
                    </div>
                    <div class="message-content">${{content}}</div>
                `;
                
                if (agentData) {{
                    html += `
                        <div class="agent-card">
                            <div class="agent-card-header">
                                <span class="agent-card-icon">📊</span>
                                <span class="agent-card-title">${{agentData.title}}</span>
                                ${{agentData.status ? `<span class="agent-card-status">${{agentData.status}}</span>` : ''}}
                            </div>
                            <div class="agent-card-content">
                                <ul class="detail-list">
                    `;
                    
                    for (const [key, value] of Object.entries(agentData.details || {{}})) {{
                        html += `
                            <li class="detail-item">
                                <span class="detail-label">${{key}}:</span>
                                <span class="detail-value">${{value}}</span>
                            </li>
                        `;
                    }}
                    
                    html += `
                                </ul>
                            </div>
                        </div>
                    `;
                }}
                
                messageDiv.innerHTML = html;
            }}

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function showTypingIndicator() {{
            const chatMessages = document.getElementById('chatMessages');
            const indicator = document.createElement('div');
            indicator.id = 'typingIndicator';
            indicator.className = 'typing-indicator';
            indicator.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        function hideTypingIndicator() {{
            const indicator = document.getElementById('typingIndicator');
            if (indicator) {{
                indicator.remove();
            }}
        }}

        function updateStatus(status, text) {{
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            statusDot.className = `status-dot ${{status}}`;
            statusText.textContent = text;
        }}

        function completeDemo() {{
            demoState.isPlaying = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('skipBtn').disabled = true;
            
            updateStatus('idle', 'Demo Complete');
        }}
    </script>
</body>
</html>'''

    def extract_agent_info(self, file_path: str) -> Dict[str, Any]:
        """Extract agent information from existing demo file or metadata"""
        agent_info = {
            'name': 'Agent',
            'icon': '🤖',
            'color': '#0078d4',
            'search_placeholder': 'Search',
            'welcome_cards': '',
            'demo_script': '[]'
        }
        
        # Try to get agent name from path
        path_parts = Path(file_path).parts
        if 'stack' in file_path:
            for part in path_parts:
                if '_stack' in part:
                    agent_name = part.replace('_stack', '').replace('_', ' ').title()
                    agent_info['name'] = agent_name
                    break
        
        # Set default welcome cards
        agent_info['welcome_cards'] = '''
            <div class="suggestion-card" onclick="quickStart('demo1')">
                <div class="card-icon">📊</div>
                <div class="card-title">Quick Demo</div>
                <div class="card-description">See the agent in action</div>
            </div>
            <div class="suggestion-card" onclick="quickStart('demo2')">
                <div class="card-icon">🎯</div>
                <div class="card-title">Use Case</div>
                <div class="card-description">Explore specific scenarios</div>
            </div>
            <div class="suggestion-card" onclick="quickStart('demo3')">
                <div class="card-icon">💡</div>
                <div class="card-title">Learn More</div>
                <div class="card-description">Understand capabilities</div>
            </div>
        '''
        
        # Set default demo script
        agent_info['demo_script'] = '''[
            {
                type: 'user',
                content: 'Show me what this agent can do',
                delay: 1000
            },
            {
                type: 'agent',
                content: 'I can help you with various tasks. Let me demonstrate my capabilities.',
                agentData: {
                    title: 'Agent Capabilities',
                    status: 'Active',
                    details: {
                        'Function': 'Automated processing',
                        'Status': 'Ready',
                        'Performance': 'Optimized'
                    }
                },
                typingTime: 2000,
                delay: 2000
            }
        ]'''
        
        return agent_info
    
    def update_demo_file(self, file_path: str) -> bool:
        """Update a single demo file to M365 Copilot pattern"""
        try:
            # Extract agent information
            agent_info = self.extract_agent_info(file_path)
            
            # Generate new content
            new_content = self.get_m365_template(
                agent_name=agent_info['name'],
                agent_icon=agent_info['icon'],
                agent_color=agent_info['color'],
                demo_script=agent_info['demo_script'],
                welcome_cards=agent_info['welcome_cards'],
                search_placeholder=agent_info['search_placeholder']
            )
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.updated_files.append(file_path)
            return True
            
        except Exception as e:
            self.failed_files.append({'file': file_path, 'error': str(e)})
            return False
    
    def perform(self, **kwargs) -> Dict[str, Any]:
        """Main execution method for the agent"""
        try:
            # Get parameters
            target_directory = kwargs.get('directory', '/Users/kodyw/Documents/GitHub/AI-Agent-Templates')
            pattern = kwargs.get('pattern', '**/demos/*_demo.html')
            
            # Find all demo files
            demo_files = []
            for root, dirs, files in os.walk(target_directory):
                for file in files:
                    if file.endswith('_demo.html') and 'demos' in root:
                        demo_files.append(os.path.join(root, file))
            
            # Update each file
            total_files = len(demo_files)
            for file_path in demo_files:
                self.update_demo_file(file_path)
            
            # Return results
            return {
                'status': 'success',
                'message': f'Updated {len(self.updated_files)} of {total_files} demo files',
                'data': {
                    'total_files': total_files,
                    'updated_files': len(self.updated_files),
                    'failed_files': len(self.failed_files),
                    'updated_list': self.updated_files[:10],  # First 10 for preview
                    'failed_list': self.failed_files
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error updating demo files: {str(e)}',
                'errors': [str(e)]
            }

# Metadata for the agent
metadata = {
    'name': 'M365 Demo Updater',
    'description': 'Updates all demo HTML files to use the M365 Copilot style pattern',
    'parameters': {
        'directory': {
            'type': 'string',
            'description': 'Target directory to scan for demo files',
            'default': '/Users/kodyw/Documents/GitHub/AI-Agent-Templates'
        },
        'pattern': {
            'type': 'string',
            'description': 'File pattern to match demo files',
            'default': '**/demos/*_demo.html'
        }
    },
    'required': []
}

# CLI execution
if __name__ == '__main__':
    agent = M365DemoUpdaterAgent()
    result = agent.perform()
    print(json.dumps(result, indent=2))