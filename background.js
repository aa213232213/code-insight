// 与本地Ollama服务通信
async function analyzeWithOllama(repoData) {
  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3.2',
        prompt: `分析仓库: ${repoData.owner}/${repoData.repo}`,
        stream: false
      })
    });
    return await response.json();
  } catch (error) {
    console.error('连接Ollama失败:', error);
    return null;
  }
}

// 处理扩展按钮点击
chrome.action.onClicked.addListener(async (tab) => {
  // 向内容脚本请求仓库信息
  const response = await chrome.tabs.sendMessage(tab.id, {action: "getRepoInfo"});
  
  if (response) {
    const analysis = await analyzeWithOllama(response);
    // 将结果显示给用户
    chrome.tabs.sendMessage(tab.id, {
      action: "showAnalysis", 
      result: analysis
    });
  }
});