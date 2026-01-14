// Modal System
const Modal = {
    init() {
        if (document.getElementById('app-modal-overlay')) return;
        
        const overlay = document.createElement('div');
        overlay.id = 'app-modal-overlay';
        overlay.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.5); z-index: 2000;
            display: none; align-items: center; justify-content: center;
            opacity: 0; transition: opacity 0.2s;
        `;
        
        const card = document.createElement('div');
        card.id = 'app-modal-card';
        card.style.cssText = `
            background: var(--bg-surface); width: 90%; max-width: 320px;
            border-radius: var(--radius-lg); padding: 24px;
            box-shadow: var(--shadow-md); transform: scale(0.95);
            transition: transform 0.2s;
        `;
        
        card.innerHTML = `
            <h3 id="modal-title" style="font-size: 18px; font-weight: 600; margin-bottom: 12px;"></h3>
            <p id="modal-msg" style="color: var(--text-secondary); font-size: 14px; margin-bottom: 24px; line-height: 1.5;"></p>
            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                <button id="modal-cancel" class="btn btn-secondary" style="flex: 1;">取消</button>
                <button id="modal-confirm" class="btn btn-primary" style="flex: 1;">确定</button>
            </div>
        `;
        
        overlay.appendChild(card);
        document.body.appendChild(overlay);
        
        this.overlay = overlay;
        this.card = card;
        this.titleEl = card.querySelector('#modal-title');
        this.msgEl = card.querySelector('#modal-msg');
        this.cancelBtn = card.querySelector('#modal-cancel');
        this.confirmBtn = card.querySelector('#modal-confirm');
    },
    
    confirm(title, message) {
        this.init();
        return new Promise((resolve) => {
            this.titleEl.textContent = title;
            this.msgEl.textContent = message;
            
            this.overlay.style.display = 'flex';
            // Force reflow
            this.overlay.offsetHeight;
            this.overlay.style.opacity = '1';
            this.card.style.transform = 'scale(1)';
            
            const close = (result) => {
                this.overlay.style.opacity = '0';
                this.card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.overlay.style.display = 'none';
                    resolve(result);
                }, 200);
            };
            
            this.confirmBtn.onclick = () => close(true);
            this.cancelBtn.onclick = () => close(false);
            this.overlay.onclick = (e) => {
                if (e.target === this.overlay) close(false);
            };
        });
    }
};

// 通用工具
const Utils = {
    async copy(text) {
        // 如果 text 是相对路径，自动转换为完整 URL
        if (text.startsWith('/')) {
            text = window.location.origin + text;
        }

        try {
            await navigator.clipboard.writeText(text);
            Toast.show('已复制到剪贴板');
            return true;
        } catch (err) {
            // Fallback for older browsers or mobile webview
            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed'; // Prevent scrolling
                textarea.style.left = '-9999px';
                textarea.style.top = '0';
                document.body.appendChild(textarea);
                textarea.focus();
                textarea.select();
                const successful = document.execCommand('copy');
                document.body.removeChild(textarea);
                if (successful) {
                    Toast.show('已复制到剪贴板');
                    return true;
                }
            } catch (fallbackErr) {
                console.error(fallbackErr);
            }
            
            // Final fallback: Select text and prompt user
            try {
                const modal = document.createElement('div');
                modal.style.cssText = `
                    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0,0,0,0.5); z-index: 9999;
                    display: flex; align-items: center; justify-content: center;
                `;
                const content = document.createElement('div');
                content.style.cssText = `
                    background: var(--bg-surface); padding: 20px; border-radius: 12px;
                    width: 90%; max-width: 300px; text-align: center;
                `;
                content.innerHTML = `
                    <p style="margin-bottom: 12px; font-weight: 500;">复制失败，请手动复制：</p>
                    <textarea readonly style="width: 100%; height: 80px; margin-bottom: 12px; padding: 8px; border: 1px solid var(--border-color); border-radius: 8px;">${text}</textarea>
                    <button class="btn btn-primary" style="width: 100%;">关闭</button>
                `;
                modal.appendChild(content);
                document.body.appendChild(modal);
                
                const ta = content.querySelector('textarea');
                ta.focus();
                ta.select();
                
                content.querySelector('button').onclick = () => modal.remove();
                modal.onclick = (e) => { if(e.target === modal) modal.remove(); };
            } catch (e) {}
            
            return false;
        }
    },
    
    setLoading(btn, isLoading) {
        if (!btn) return;
        if (isLoading) {
            btn.dataset.originalText = btn.innerHTML;
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> 处理中...`;
            btn.classList.add('loading');
            btn.disabled = true;
        } else {
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    }
};

// 复制文件链接的辅助函数
window.copyLink = (shortId, fileId, filename) => {
    let path;
    if (shortId && shortId !== 'None' && shortId !== '') {
        path = `/d/${shortId}`;
    } else {
        path = `/d/${fileId}/${encodeURIComponent(filename)}`;
    }
    Utils.copy(path);
};

// 认证系统
const Auth = {
    async logout() {
        const confirmed = await Modal.confirm('退出登录', '确定要退出当前账号吗？');
        if (!confirmed) return;
        
        try {
            const res = await fetch('/api/auth/logout', {
                method: 'POST',
                // 确保携带凭证（Cookies）
                credentials: 'include' 
            });
            
            if (res.ok) {
                // 清理可能存在的本地状态
                // localStorage.removeItem('some_key'); 
                
                // 强制跳转到登录页，并替换历史记录，防止后退
                window.location.replace('/login');
            } else {
                Toast.show('退出失败，请刷新重试', 'error');
            }
        } catch (e) {
            console.error(e);
            Toast.show('网络错误', 'error');
        }
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    Theme.init();
    
    // 侧边栏/移动端菜单切换

    const toggleBtn = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
        });
    }
    
    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }
});
