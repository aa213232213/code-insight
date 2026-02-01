// 在GitHub页面添加触发按钮
function addTriggerButton() {
  if (document.getElementById('code-insight-trigger')) return;

  const triggerBtn = document.createElement('button');
  triggerBtn.id = 'code-insight-trigger';
  triggerBtn.innerHTML = '🔍 Insight';
  triggerBtn.style.cssText = `
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 999;
    background: #1a7f37;
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    transition: all 0.2s;
  `;

  triggerBtn.addEventListener('mouseenter', () => {
    triggerBtn.style.background = '#196c2f';
    triggerBtn.style.transform = 'translateY(-1px)';
  });

  triggerBtn.addEventListener('mouseleave', () => {
    triggerBtn.style.background = '#1a7f37';
    triggerBtn.style.transform = 'translateY(0)';
  });

  triggerBtn.addEventListener('click', injectSidebar);
  document.body.appendChild(triggerBtn);
}

// 模型配置
const OLLAMA_MODELS = [
  {
    "title": "🚀 DeepSeek Coder 6.7B (本地)",
    "provider": "ollama", 
    "model": "deepseek-coder:6.7b",
    "description": "编程专用 - 快速响应"
  },
  {
    "title": "🧠 GPT 20B (本地)",
    "provider": "ollama",
    "model": "gpt-oss:20b", 
    "description": "200亿参数 - 平衡的本地模型"
  },
  {
    "title": "💫 DeepSeek R1 8B (本地)",
    "provider": "ollama",
    "model": "deepseek-r1:8b",
    "description": "推理优化 - 快速问答"
  },
  {
    "title": "🦙 Llama 3.2 (本地)",
    "provider": "ollama",
    "model": "llama3.2:latest",
    "description": "Meta开源 - 稳定通用"
  },
  {
    "title": "🔥 DeepSeek V3.1 671B (云)",
    "provider": "ollama", 
    "model": "deepseek-v3.1:671b-cloud",
    "description": "6710亿参数 - 最强推理"
  },
  {
    "title": "💻 Qwen Coder 480B (云)",
    "provider": "ollama",
    "model": "qwen3-coder:480b-cloud",
    "description": "4800亿参数 - 编程专精"
  },
  {
    "title": "🧠 GPT OSS 120B (云)",
    "provider": "ollama",
    "model": "gpt-oss:120b-cloud",
    "description": "1200亿参数 - 通用对话"
  },
  {
    "title": "🌐 GLM 4.6 (云)",
    "provider": "ollama",
    "model": "glm-4.6:cloud",
    "description": "智谱AI - 中文优秀"
  },
  {
    "title": "🌟 Kimi K2 (云)", 
    "provider": "ollama",
    "model": "kimi-k2:1t-cloud",
    "description": "Kimi模型 - 中文理解"
  }
];

// 注入侧边栏
function injectSidebar() {
  if (document.getElementById('code-insight-sidebar')) return;

  const sidebar = document.createElement('div');
  sidebar.id = 'code-insight-sidebar';
  sidebar.className = 'code-insight-sidebar';
  sidebar.innerHTML = `
    <div class="sidebar-header">
      <h3>🔍 Code Insight</h3>
      <button class="close-btn" title="关闭">&times;</button>
    </div>
    <div class="sidebar-content">
      <p>一键分析当前 GitHub 代码库，获取项目架构和使用场景分析</p>
      
      <div class="model-selector">
        <label for="model-select">选择 AI 模型：</label>
        <select id="model-select" class="model-select">
          ${OLLAMA_MODELS.map(model => 
            `<option value="${model.model}" data-description="${model.description}">${model.title}</option>`
          ).join('')}
        </select>
        <div class="model-description" id="model-description">${OLLAMA_MODELS[0].description}</div>
      </div>
      
      <button class="analyze-btn" id="analyze-btn">开始分析</button>
      
      <div id="loading" class="loading" style="display: none;">
        <div class="loading-spinner"></div>
        <div>正在分析代码库...</div>
        <small>这可能需要 30-60 秒，请耐心等待</small>
      </div>
      
      <div id="result-container" style="display: none;">
        <div class="analysis-result">
          <h4 id="result-title">分析结果</h4>
          <div class="analysis-content" id="analysis-result"></div>
          <div class="file-info" id="file-info"></div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(sidebar);

  // 事件监听
  sidebar.querySelector('.close-btn').addEventListener('click', () => {
    sidebar.remove();
  });

  sidebar.querySelector('#analyze-btn').addEventListener('click', analyzeCurrentRepo);
  
  // 添加模型描述更新
  const modelSelect = sidebar.querySelector('#model-select');
  const modelDescription = sidebar.querySelector('#model-description');
  
  modelSelect.addEventListener('change', (e) => {
    const selectedOption = modelSelect.options[modelSelect.selectedIndex];
    modelDescription.textContent = selectedOption.getAttribute('data-description');
  });
}

// 完整的 Markdown 解析器
class MarkdownParser {
  static parse(markdownText) {
    if (!markdownText) return '';
    
    let html = markdownText;
    
    // 处理代码块
    html = this.parseCodeBlocks(html);
    
    // 处理内联代码
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 处理标题
    html = this.parseHeaders(html);
    
    // 处理粗体和斜体
    html = this.parseEmphasis(html);
    
    // 处理列表
    html = this.parseLists(html);
    
    // 处理链接
    html = this.parseLinks(html);
    
    // 处理引用
    html = this.parseBlockquotes(html);
    
    // 处理水平线
    html = html.replace(/^\s*---\s*$/gm, '<hr>');
    
    // 处理段落和换行
    html = this.parseParagraphs(html);
    
    return html;
  }

  static parseCodeBlocks(text) {
    return text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      const language = lang || 'text';
      return `<pre class="code-block language-${language}"><code>${this.escapeHtml(code.trim())}</code></pre>`;
    });
  }

  static parseHeaders(text) {
    // h1
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    // h2
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    // h3
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    // h4
    text = text.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    // h5
    text = text.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
    // h6
    text = text.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
    
    return text;
  }

  static parseEmphasis(text) {
    // 粗体 **text** 或 __text__
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // 斜体 *text* 或 _text_
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // 删除线 ~~text~~
    text = text.replace(/~~(.*?)~~/g, '<del>$1</del>');
    
    return text;
  }

  static parseLists(text) {
    // 无序列表
    text = text.replace(/^\s*[-*+] (.*)$/gim, '<li>$1</li>');
    
    // 有序列表
    text = text.replace(/^\s*\d+\. (.*)$/gim, '<li>$1</li>');
    
    // 包装列表项
    text = text.replace(/(<li>.*<\/li>)/gs, (match) => {
      // 检查是否已经包装在ul/ol中
      if (!match.startsWith('<ul>') && !match.startsWith('<ol>')) {
        // 检查第一个列表项是否是数字开头，决定使用ol还是ul
        const firstItem = match.match(/<li>(\d+)\./);
        if (firstItem) {
          return `<ol>${match}</ol>`;
        } else {
          return `<ul>${match}</ul>`;
        }
      }
      return match;
    });
    
    return text;
  }

  static parseLinks(text) {
    // [text](url)
    return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }

  static parseBlockquotes(text) {
    return text.replace(/^> (.*)$/gim, '<blockquote>$1</blockquote>');
  }

  static parseParagraphs(text) {
    // 分割成段落
    const paragraphs = text.split(/\n\s*\n/);
    
    return paragraphs.map(paragraph => {
      paragraph = paragraph.trim();
      if (!paragraph) return '';
      
      // 如果已经是HTML标签，直接返回
      if (paragraph.startsWith('<') && 
          (paragraph.includes('<h') || 
           paragraph.includes('<ul') || 
           paragraph.includes('<ol') || 
           paragraph.includes('<pre') || 
           paragraph.includes('<blockquote') || 
           paragraph.includes('<hr'))) {
        return paragraph;
      }
      
      // 处理段落内的换行
      paragraph = paragraph.replace(/\n/g, '<br>');
      
      return `<p>${paragraph}</p>`;
    }).join('');
  }

  static escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// 简单的代码块高亮函数
function highlightCodeBlocks(container) {
  try {
    const codeBlocks = container.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
      const text = block.textContent;
      // 简单的关键词高亮
      let highlighted = text
        .replace(/(function|class|const|let|var|return|if|else|for|while|import|export|from)(?=\s)/g, '<span class="keyword">$1</span>')
        .replace(/(true|false|null|undefined)(?=\s|;|\)|,)/g, '<span class="literal">$1</span>')
        .replace(/(\/\/.*$)/gm, '<span class="comment">$1</span>')
        .replace(/(\d+)/g, '<span class="number">$1</span>');
      
      block.innerHTML = highlighted;
    });
  } catch (error) {
    console.warn('代码高亮处理失败:', error);
  }
}

// 分析当前仓库
async function analyzeCurrentRepo() {
  const btn = document.getElementById('analyze-btn');
  const loading = document.getElementById('loading');
  const resultContainer = document.getElementById('result-container');
  const resultDiv = document.getElementById('analysis-result');
  const fileInfoDiv = document.getElementById('file-info');
  const resultTitle = document.getElementById('result-title');
  const modelSelect = document.getElementById('model-select');
  
  const selectedModel = modelSelect.value;

  // 更新按钮状态
  btn.textContent = '分析中...';
  btn.disabled = true;
  loading.style.display = 'block';
  resultContainer.style.display = 'none';
  resultDiv.innerHTML = ''; // 清空之前的结果

  try {
    const currentUrl = window.location.href;
    console.log(`开始分析: ${currentUrl}, 使用模型: ${selectedModel}`);
    
    const response = await fetch('http://localhost:5000/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        url: currentUrl,
        model: selectedModel
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP错误! 状态码: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      resultTitle.textContent = `分析结果: ${data.data.repo_name}`;
      
      // 使用 Markdown 解析器格式化结果
      const formattedAnalysis = MarkdownParser.parse(data.data.analysis);
      resultDiv.innerHTML = formattedAnalysis;
      
      fileInfoDiv.innerHTML = `
        <div class="file-stats">
          <span class="stat-item">📊 分析了 <strong>${data.data.file_count}</strong> 个代码文件</span>
          <span class="stat-item">🤖 使用模型: <strong>${selectedModel}</strong></span>
        </div>
      `;
      
      resultContainer.style.display = 'block';
      
      // 添加语法高亮
      highlightCodeBlocks(resultDiv);
    } else {
      throw new Error(data.error || '分析失败');
    }
  } catch (error) {
    // 修复：安全的错误日志记录和显示
    try {
      console.error('分析失败:', error);
    } catch (logError) {
      // 如果 console.error 也失败，静默处理
    }
    
    // 安全地显示错误信息
    let errorMessage = '未知错误，请检查控制台';
    try {
      errorMessage = error.message || String(error);
    } catch (e) {
      // 如果提取错误信息失败，使用默认消息
    }
    
    try {
      resultDiv.innerHTML = `
        <div class="error-message">
          <div class="error-icon">❌</div>
          <div class="error-content">
            <strong>分析失败</strong><br><br>
            错误信息: ${errorMessage}<br><br>
            可能的原因:<br>
            • Python 服务未运行 (http://localhost:5000)<br>
            • Ollama 服务未启动<br>
            • 网络连接问题<br>
            • 防火墙阻止了连接
          </div>
        </div>
      `;
      fileInfoDiv.textContent = '';
      resultContainer.style.display = 'block';
    } catch (displayError) {
      // 如果显示错误也失败，使用最简单的错误显示
      resultDiv.textContent = '分析过程中发生错误';
      resultContainer.style.display = 'block';
    }
  } finally {
    try {
      loading.style.display = 'none';
      btn.textContent = '开始分析';
      btn.disabled = false;
    } catch (finalError) {
      // 确保最终状态恢复，即使出错
    }
  }
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addTriggerButton);
} else {
  addTriggerButton();
}

// 处理页面动态加载（如 GitHub 的 PJAX 导航）
let currentUrl = window.location.href;
setInterval(() => {
  if (window.location.href !== currentUrl) {
    currentUrl = window.location.href;
    // 移除旧的触发按钮（如果存在）
    const oldBtn = document.getElementById('code-insight-trigger');
    if (oldBtn) oldBtn.remove();
    // 重新添加按钮
    addTriggerButton();
  }
}, 1000);