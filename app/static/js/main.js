document.addEventListener('DOMContentLoaded', () => {
    // --- Global Variables ---
    const uploadArea = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-picker');
    const progressArea = document.getElementById('prog-zone');
    const doneArea = document.getElementById('done-zone');
    const searchInput = document.getElementById('file-search');
    
    // --- Copy Link Delegation ---
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.copy-link-btn');
        if (!btn) return;
        
        // Prevent default if it's a link (though it's a button)
        e.preventDefault();
        e.stopPropagation();

        const item = btn.closest('.file-item, .image-card');
        if (!item) return; // Should exist
        
        // 如果按钮上有 onclick 属性（旧代码或特殊情况），优先执行 onclick，这里不处理
        if (btn.hasAttribute('onclick')) return;

        const shortId = item.dataset.shortId;
        const fileId = item.dataset.fileId;
        const filename = item.dataset.filename;
        
        // 核心策略：优先从 DOM 中获取真实可用的绝对 URL
        let url = '';

        // 1. 尝试获取下载按钮的链接 (文件列表模式)
        // 查找 href 以 /d/ 开头的 a 标签
        const downloadLink = item.querySelector('a[href^="/d/"]');
        if (downloadLink && downloadLink.href) {
            url = downloadLink.href;
        }
        
        // 2. 尝试获取图片的 src (图床模式)
        if (!url) {
            const img = item.querySelector('img[src^="/d/"]');
            if (img && img.src) {
                url = img.src;
            }
        }

        // 3. Fallback: 使用 dataset 中的 fileUrl (如果存在且非空且不是 undefined 字符串)
        if (!url) {
            const dsUrl = item.dataset.fileUrl;
            if (dsUrl && dsUrl !== 'undefined') {
                url = dsUrl;
                // 确保是绝对路径
                if (url.startsWith('/')) {
                    url = window.location.origin + url;
                }
            }
        }
        
        // 4. Final Fallback: 构造 /d/{id}
        if (!url || url.includes('undefined')) {
             const id = (shortId && shortId !== 'None' && shortId !== '') ? shortId : fileId;
             url = window.location.origin + `/d/${id}`;
        }
        
        // 安全检查：如果最终结果包含 undefined，强制重构
        if (url.includes('undefined')) {
            // 最后的兜底，哪怕 fileId 也是 undefined (极低概率)，也比 http://...undefined 好
             console.warn('Constructed URL contained undefined, falling back to raw fileId');
             url = window.location.origin + '/d/' + (fileId || 'error');
        }

        if (window.copyLink) {
             Utils.copy(url);
        } else {
             Utils.copy(url);
        }
    });

    // Sort state managed in memory instead of dropdowns
    let currentSort = {
        field: localStorage.getItem('file-sort-by') || 'upload_date',
        order: localStorage.getItem('file-sort-order') || 'desc'
    };


    // --- File Fetching and Rendering ---
    async function fetchAndRenderFiles(category = '', searchTerm = '', sortBy = 'upload_date', sortOrder = 'desc') { // Added sortBy, sortOrder
        const fileListDisk = document.getElementById('file-list-disk');
        if (!fileListDisk) return; // Not on the main files page

        fileListDisk.innerHTML = '<tr><td colspan="5" style="padding: 48px; text-align: center;"><div class="text-muted">加载文件...</div></td></tr>';

        let url = '/api/files?';
        if (category) url += `category=${category}&`;
        if (searchTerm) url += `search=${searchTerm}&`;
        if (sortBy) url += `sort_by=${sortBy}&`; // Add sortBy
        if (sortOrder) url += `sort_order=${sortOrder}&`; // Add sortOrder
        url = url.slice(0, -1); // Remove trailing '&' or '?'

        try {
            const response = await fetch(url);
            if (!response.ok) {
                // Handle non-200 responses, e.g., 401 Unauthorized
                const errorData = await response.json();
                throw new Error(errorData.detail?.message || `API error: ${response.status}`);
            }
            const files = await response.json(); // Assuming API directly returns list of files

            fileListDisk.innerHTML = ''; // Clear previous content

            if (files.length === 0) {
                fileListDisk.innerHTML = '<tr><td colspan="5" style="padding: 48px; text-align: center;"><div class="text-muted">暂无文件</div></td></tr>';
                return;
            }

            files.forEach(file => addNewFileElement(file, 'beforeend')); // Pass position to append
            // Remove empty state if exists, after adding files (redundant if fileListDisk.innerHTML is cleared)
            // const emptyState = fileListDisk.querySelector('div[style*="text-align: center"]');
            // if (emptyState) emptyState.remove();

        } catch (error) {
            console.error('Error fetching files:', error);
            fileListDisk.innerHTML = `<tr><td colspan="5" style="padding: 48px; text-align: center;"><div style="color: var(--danger-color);">加载文件失败: ${error.message}</div></td></tr>`;
        }
        updateBatchControls(); // Update batch controls after files are rendered
    }

    // --- Search & Category & Sort Functionality ---
    const applyFiltersAndSort = () => {
        const term = searchInput ? searchInput.value : '';
        const activeTab = document.querySelector('.category-tab.active');
        const category = activeTab ? (activeTab.dataset.category || '') : '';
        
        // Save sort preferences to LocalStorage
        localStorage.setItem('file-sort-by', currentSort.field);
        localStorage.setItem('file-sort-order', currentSort.order);

        fetchAndRenderFiles(category, term, currentSort.field, currentSort.order);
    };

    // Update visual indicators for initial sort
    document.querySelectorAll('.sortable-header').forEach(h => h.classList.remove('active'));
    document.querySelectorAll('.sort-icon').forEach(icon => {
        icon.classList.remove('active', 'asc', 'desc');
        icon.style.opacity = '0.3';
        icon.style.color = '';
    });
    const activeHeader = document.querySelector(`.sortable-header[data-sort="${currentSort.field}"]`);
    if (activeHeader) {
        activeHeader.classList.add('active');
        const icon = activeHeader.querySelector('.sort-icon');
        if (icon) {
            icon.classList.add('active', currentSort.order);
            icon.style.opacity = '1';
            icon.style.color = 'var(--primary-color)';
        }
    }


    if (searchInput) {
        searchInput.addEventListener('input', applyFiltersAndSort);
    }

    // Category Tab switching
    document.addEventListener('click', (e) => {
        const tab = e.target.closest('.category-tab');
        if (!tab) return;

        // Update active state
        document.querySelectorAll('.category-tab').forEach(t => {
            t.classList.remove('active');
        });
        tab.classList.add('active');

        // Refresh file list with selected category
        applyFiltersAndSort();
    });

    // Category Tab switching

    // Table header sorting
    document.addEventListener('click', (e) => {
        const header = e.target.closest('.sortable-header');
        if (!header) return;

        const sortField = header.dataset.sort;

        // If clicking same column, toggle order; otherwise default to desc
        if (sortField === currentSort.field) {
            currentSort.order = currentSort.order === 'desc' ? 'asc' : 'desc';
        } else {
            currentSort.field = sortField;
            currentSort.order = 'desc';
        }

        // Update visual indicators
        document.querySelectorAll('.sortable-header').forEach(h => h.classList.remove('active'));
        document.querySelectorAll('.sort-icon').forEach(icon => {
            icon.classList.remove('active', 'asc', 'desc');
            icon.style.opacity = '0.3';
            icon.style.color = '';
        });
        header.classList.add('active');
        const icon = header.querySelector('.sort-icon');
        icon.classList.add('active', currentSort.order);
        icon.style.opacity = '1';
        icon.style.color = 'var(--primary-color)';

        // Apply sorting
        applyFiltersAndSort();
    });


    // --- Upload Logic ---
    const uploadButton = document.getElementById('upload-button');
    if (uploadButton && fileInput) {
        uploadButton.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', ({ target }) => {
            console.log('DEBUG: fileInput change event triggered. Files:', target.files);
            if (target.files.length > 0) {
                handleFiles(target.files);
            }
        });
    }

    // Drag and drop logic - this should still apply to the document or a specific drop zone if desired,
    // but the original 'uploadArea' card is now gone.
    // If drag and drop is still desired for the new compact design, a new drop zone needs to be defined.
    // For now, let's remove the drag and drop listeners that were tied to the old uploadArea.

    // Queue system for uploads

    // Queue system for uploads
    const uploadQueue = [];
    let isUploading = false;

    function handleFiles(files) {
        console.log('DEBUG: handleFiles called with files:', files);
        if (progressArea) {
            progressArea.innerHTML = '';
            progressArea.style.display = 'flex'; // Show prog-zone when uploads start
        }

        for (const file of files) {
            uploadQueue.push(file);
        }
        processQueue();
    }

    function processQueue() {
        if (isUploading || uploadQueue.length === 0) {
            if (uploadQueue.length === 0 && !isUploading && progressArea) {
                progressArea.style.display = 'none'; // Hide prog-zone if queue is empty
            }
            return;
        }

        isUploading = true;
        const file = uploadQueue.shift();
        uploadFile(file).then(() => {
            isUploading = false;
            processQueue();
        });
    }

    function uploadFile(file) {
        return new Promise((resolve) => {
            const formData = new FormData();
            formData.append('file', file, file.name);
            
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/api/upload', true);
            const fileId = `temp-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;

            // Initial Progress UI
            // 使用新版 UI 风格
            const progressHTML = `
                <div class="card" id="progress-${fileId}" style="padding: 16px; margin-bottom: 12px; border: 1px solid var(--border-color);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 14px; font-weight: 500;">${file.name}</span>
                        <span class="percent" style="font-size: 12px; color: var(--text-secondary);">0%</span>
                    </div>
                    <div style="height: 4px; background: var(--bg-surface-hover); border-radius: 2px; overflow: hidden;">
                        <div class="progress-bar" style="width: 0%; height: 100%; background: var(--primary-color); transition: width 0.2s;"></div>
                    </div>
                </div>`;
            
            if (progressArea) progressArea.insertAdjacentHTML('beforeend', progressHTML);
            const progressEl = document.querySelector(`#progress-${fileId} .progress-bar`);
            const percentEl = document.querySelector(`#progress-${fileId} .percent`);

            xhr.upload.onprogress = ({ loaded, total }) => {
                const percent = Math.floor((loaded / total) * 100);
                if (progressEl) progressEl.style.width = `${percent}%`;
                if (percentEl) percentEl.textContent = `${percent}%`;
            };

            xhr.onload = () => {
                const progressRow = document.getElementById(`progress-${fileId}`);
                if (progressRow) progressRow.remove();

                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    const fileUrl = response.url;
                    
                    // Success Toast
                    if (window.Toast) Toast.show(`${file.name} 上传成功`);
                    
                    // Add to done area
                    const successHTML = `
                        <div class="card" style="padding: 16px; margin-bottom: 12px; border-left: 4px solid var(--success-color);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="overflow: hidden; margin-right: 12px;">
                                    <div style="font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${file.name}</div>
                                    <a href="${fileUrl}" target="_blank" style="font-size: 12px; color: var(--primary-color);">${fileUrl}</a>
                                </div>
                                <button class="btn btn-secondary btn-sm" onclick="Utils.copy('${fileUrl}')">复制</button>
                            </div>
                        </div>`;
                    if (doneArea) doneArea.insertAdjacentHTML('afterbegin', successHTML);
                } else {
                    let errorMsg = "上传失败";
                    try {
                        const parsed = JSON.parse(xhr.responseText);
                        const detail = parsed && parsed.detail;
                        if (typeof detail === 'string') {
                            errorMsg = detail;
                        } else if (detail && typeof detail === 'object') {
                            errorMsg = detail.message || errorMsg;
                        } else if (parsed && parsed.message) {
                            errorMsg = parsed.message;
                        }
                    } catch (e) {}
                    
                    if (window.Toast) Toast.show(errorMsg, 'error');
                }
                resolve();
            };

            xhr.onerror = () => {
                const progressRow = document.getElementById(`progress-${fileId}`);
                if (progressRow) progressRow.remove();
                if (window.Toast) Toast.show('网络错误', 'error');
                resolve();
            };

            xhr.send(formData);
        });
    }

    // --- Batch Actions ---
    const selectAllCheckbox = document.getElementById('select-all-checkbox');
    const batchDeleteBtn = document.getElementById('batch-delete-btn');
    const copyLinksBtn = document.getElementById('copy-links-btn');
    const selectionCounter = document.getElementById('selection-counter');
    const batchActionsBar = document.getElementById('batch-actions-bar');
    const formatOptions = document.querySelectorAll('.format-option');

    function updateBatchControls() {
        const checkboxes = document.querySelectorAll('.file-checkbox');
        const checked = document.querySelectorAll('.file-checkbox:checked');
        const count = checked.length;
        
        if (selectionCounter) selectionCounter.textContent = count > 0 ? `${count} 项已选` : '0 项已选';
        
        if (batchActionsBar) {
            if (count > 0) {
                batchActionsBar.classList.remove('hidden');
            } else {
                batchActionsBar.classList.add('hidden');
            }
        }

        if (selectAllCheckbox) selectAllCheckbox.checked = (count > 0 && count === checkboxes.length);
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            document.querySelectorAll('.file-checkbox').forEach(cb => {
                cb.checked = e.target.checked;
            });
            updateBatchControls();
        });
    }

    // Delegation for dynamic checkboxes
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('file-checkbox')) {
            updateBatchControls();
        }
    });

    // Format selection (Image Hosting)
    if (formatOptions) {
        formatOptions.forEach(opt => {
            opt.addEventListener('click', () => {
                formatOptions.forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
            });
        });
    }

    // Batch Copy
    if (copyLinksBtn) {
        copyLinksBtn.addEventListener('click', () => {
            const checked = document.querySelectorAll('.file-checkbox:checked');
            if (checked.length === 0) return;

            const activeFormatBtn = document.querySelector('.format-option.active');
            const format = activeFormatBtn ? activeFormatBtn.dataset.format : 'url';
            
            const links = Array.from(checked).map(cb => {
                const item = cb.closest('.file-item, .image-card');
                let url = '';

                // 1. 尝试获取下载按钮
                const downloadLink = item.querySelector('a[href^="/d/"]');
                if (downloadLink && downloadLink.href) {
                    url = downloadLink.href;
                }
                
                // 2. 尝试获取图片 src
                if (!url) {
                    const img = item.querySelector('img[src^="/d/"]');
                    if (img && img.src) {
                        url = img.src;
                    }
                }
                
                // 3. Fallback: Dataset
                if (!url) {
                    const dsUrl = item.dataset.fileUrl;
                    if (dsUrl && dsUrl !== 'undefined') {
                        url = dsUrl;
                        if (url.startsWith('/')) {
                            url = window.location.origin + url;
                        }
                    }
                }
                
                // 4. Final Fallback
                if (!url || url.includes('undefined')) {
                    const shortId = item.dataset.shortId;
                    const fileId = item.dataset.fileId;
                    const id = (shortId && shortId !== 'None' && shortId !== '') ? shortId : fileId;
                    url = window.location.origin + `/d/${id}`;
                }
                
                const name = item.dataset.filename;

                if (format === 'markdown') return `![${name}](${url})`;
                if (format === 'html') return `<img src="${url}" alt="${name}">`;
                return url;
            });

            Utils.copy(links.join('\n'));
        });
    }

    // Batch Delete
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', async () => {
            const checked = document.querySelectorAll('.file-checkbox:checked');
            if (checked.length === 0) return;

            const confirmed = await Modal.confirm('批量删除', `确定要删除选中的 ${checked.length} 个文件吗？`);
            if (!confirmed) return;

            const fileIds = Array.from(checked).map(cb => cb.dataset.fileId);
            
            fetch('/api/batch_delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_ids: fileIds })
            })
            .then(res => res.json())
            .then(data => {
                if (data.deleted) {
                    data.deleted.forEach(item => {
                         const id = item.details?.file_id || item; 
                         removeFileElement(id);
                    });
                    if (window.Toast) Toast.show(`已删除 ${data.deleted.length} 个文件`);
                }
                updateBatchControls();
            });
        });
    }

    // --- SSE & Realtime Updates ---
    const fileListContainer = document.getElementById('file-list-disk');
    if (fileListContainer) {
        // Initial fetch on load, applying current filter and sort selections
        const activeTab = document.querySelector('.category-tab.active');
        const initialCategory = activeTab ? (activeTab.dataset.category || '') : '';
        fetchAndRenderFiles(initialCategory, '', currentSort.field, currentSort.order);
        
        let eventSource = null;

        const connectSSE = () => {
            if (eventSource) {
                eventSource.close();
            }
            eventSource = new EventSource('/api/file-updates');

            eventSource.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                const action = msg && msg.action ? msg.action : 'add';
                if (action === 'delete') {
                    removeFileElement(msg.file_id);
                    updateBatchControls();
                    return;
                }
                addNewFileElement(msg, 'afterbegin'); // Prepend new files
            };

            eventSource.onerror = () => {
                try { eventSource.close(); } catch (_) {}
                setTimeout(connectSSE, 5000);
            };
        };

        // Connect SSE after initial file fetch
        connectSSE();
    }

    function formatDateValue(value) {
        if (!value) return '';
        const d = new Date(value);
        if (!isNaN(d.getTime())) return d.toISOString().split('T')[0];
        const s = String(value);
        return s.split(' ')[0].split('T')[0];
    }

    function addNewFileElement(file, position = 'afterbegin') { // Default to afterbegin for new uploads
        const isGridView = document.querySelector('.image-grid') !== null;
        const container = document.getElementById('file-list-disk');
        if (!container) return; // Not on the file list page

        // Remove empty state if exists
        const emptyState = container.querySelector('div[style*="text-align: center"]');
        if (emptyState) emptyState.remove();

        const formattedSize = (file.filesize / (1024 * 1024)).toFixed(2) + " MB";
        const formattedDate = formatDateValue(file.upload_date);
        const safeId = file.file_id.replace(':', '-');
        
        // URL construction: Always use /d/{file_id} (short_id preferred)
        // 回滚：只使用 /d/{id} 格式，不再拼接文件名或 slug
        let fileUrl = `/d/${file.short_id || file.file_id}`;

        let html = '';
        if (isGridView) {
             // 判断是否为图片类型，使用缩略图
             const mimeType = file.mime_type || '';
             const isImage = mimeType.startsWith('image/');
             const imgSrc = isImage
                ? `/api/thumbnail/${file.short_id || file.file_id}?size=medium`
                : fileUrl;
             const imgOnerror = isImage ? `onerror="this.src='${fileUrl}'"` : '';

             html = `
                <div class="file-item image-card clickable-file-row" style="border: 1px solid var(--border-color); border-radius: var(--radius-md); overflow: hidden; background: var(--bg-body);" id="file-item-${safeId}" data-file-id="${file.file_id}" data-file-url="${fileUrl}" data-filename="${file.filename}" data-short-id="${file.short_id || ''}" data-file-type="${mimeType}">
                    <div style="position: relative; aspect-ratio: 16/9; background: #000;">
                        <img src="${imgSrc}" loading="lazy" style="width: 100%; height: 100%; object-fit: contain;" alt="${file.filename}" ${imgOnerror}>
                        <div style="position: absolute; top: 8px; left: 8px;">
                            <input type="checkbox" class="file-checkbox" data-file-id="${file.file_id}" style="width: 16px; height: 16px; cursor: pointer;" onclick="event.stopPropagation()">
                        </div>
                    </div>
                    <div style="padding: 12px;">
                        <div class="text-sm font-medium" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px;" title="${file.filename}">${file.filename}</div>
                        <div class="text-sm text-muted" style="margin-bottom: 12px;">${formattedSize}</div>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn btn-secondary btn-sm copy-link-btn" style="flex: 1; height: 32px;">复制</button>
                            <button class="btn btn-secondary btn-sm delete" style="height: 32px; color: var(--danger-color);" onclick="deleteFile('${file.file_id}')">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </div>
                </div>`;
        } else {
            html = `
                <tr class="file-item clickable-file-row" style="border-bottom: 1px solid var(--border-color);" id="file-item-${safeId}" data-file-id="${file.file_id}" data-file-url="${fileUrl}" data-filename="${file.filename}" data-short-id="${file.short_id || ''}" data-file-type="${file.mime_type || 'application/octet-stream'}">
                    <td style="padding: 12px 16px;"><input type="checkbox" class="file-checkbox" data-file-id="${file.file_id}"></td>
                    <td style="padding: 12px 16px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--primary-color);"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
                            <span class="text-sm font-medium" style="color: var(--text-primary);">${file.filename}</span>
                        </div>
                    </td>
                    <td style="padding: 12px 16px;" class="text-sm text-muted">${formattedSize}</td>
                    <td style="padding: 12px 16px;" class="text-sm text-muted">${formattedDate}</td>
                    <td style="padding: 12px 16px; text-align: right;">
                        <div style="display: flex; justify-content: flex-end; gap: 8px;">
                            <a href="${fileUrl}" class="btn btn-ghost" style="padding: 4px 8px; height: 28px;" title="下载">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                            </a>
                            <button class="btn btn-ghost copy-link-btn" style="padding: 4px 8px; height: 28px;" title="复制链接">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            </button>
                            <button class="btn btn-ghost delete" style="padding: 4px 8px; height: 28px; color: var(--danger-color);" onclick="deleteFile('${file.file_id}')" title="删除">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                </tr>`;
        }

        container.insertAdjacentHTML(position, html); // Use position
    }

    // --- File Preview Logic ---
    const filePreviewModal = document.getElementById('file-preview-modal');
    const previewImage = document.getElementById('preview-image');
    const previewVideo = document.getElementById('preview-video');
    const previewIframe = document.getElementById('preview-iframe');
    const previewUnsupported = document.getElementById('preview-unsupported');
    const previewDownloadLink = document.getElementById('preview-download-link');
    const previewLoading = document.getElementById('preview-loading'); // New variable
    const previewCloseButton = filePreviewModal ? filePreviewModal.querySelector('.close-button') : null;

    function resetPreviewModal() {
        if (previewImage) previewImage.style.display = 'none';
        if (previewVideo) previewVideo.style.display = 'none';
        if (previewIframe) previewIframe.style.display = 'none';
        if (previewUnsupported) previewUnsupported.style.display = 'none';
        if (previewLoading) previewLoading.style.display = 'none'; // Hide loading on reset

        if (previewImage) previewImage.src = '';
        if (previewVideo) previewVideo.src = '';
        if (previewIframe) previewIframe.src = '';
        if (previewVideo) previewVideo.pause(); // Pause video playback
    }

    function openPreviewModal(fileUrl, fileType, fileName) {
        if (!filePreviewModal) return;

        resetPreviewModal();
        filePreviewModal.style.display = 'flex';

        // Always show loading first
        if (previewLoading) {
            previewLoading.style.display = 'flex';
        }

        let supported = false;

        if (fileType.startsWith('image/')) {
            if (previewImage) {
                previewImage.onload = () => {
                    if (previewLoading) previewLoading.style.display = 'none';
                };
                previewImage.onerror = () => {
                    if (previewLoading) previewLoading.style.display = 'none';
                    if (previewUnsupported) previewUnsupported.style.display = 'block';
                };
                previewImage.src = fileUrl;
                previewImage.style.display = 'block';
            }
            supported = true;
        } else if (fileType.startsWith('video/') || fileType.startsWith('audio/')) {
            if (previewVideo) {
                previewVideo.onloadeddata = () => {
                    if (previewLoading) previewLoading.style.display = 'none';
                };
                previewVideo.onerror = () => {
                    if (previewLoading) previewLoading.style.display = 'none';
                    if (previewUnsupported) previewUnsupported.style.display = 'block';
                };
                previewVideo.src = fileUrl;
                previewVideo.style.display = 'block';
                previewVideo.load();
                previewVideo.play();
            }
            supported = true;
        } else if (fileType === 'application/pdf' || fileType.startsWith('text/')) {
            if (previewIframe) {
                previewIframe.onload = () => {
                    if (previewLoading) previewLoading.style.display = 'none';
                };
                previewIframe.onerror = () => {
                    if (previewLoading) previewLoading.style.display = 'none';
                    if (previewUnsupported) previewUnsupported.style.display = 'block';
                };
                previewIframe.src = fileUrl;
                previewIframe.style.display = 'block';
            }
            supported = true;
        }

        if (!supported) {
            if (previewUnsupported) previewUnsupported.style.display = 'block';
            if (previewLoading) previewLoading.style.display = 'none';
        }
    }

    function closePreviewModal() {
        if (filePreviewModal) {
            filePreviewModal.style.display = 'none';
            resetPreviewModal();
        }
    }

    if (previewCloseButton) {
        previewCloseButton.addEventListener('click', closePreviewModal);
    }
    // Close modal if user clicks outside of modal-content
    if (filePreviewModal) {
        filePreviewModal.addEventListener('click', (e) => {
            if (e.target === filePreviewModal) {
                closePreviewModal();
            }
        });
    }

    // Attach click listener to file items
    document.addEventListener('click', (e) => {
        const fileRow = e.target.closest('.clickable-file-row');
        // Ensure the click wasn't on a child button/link (handled by event.stopPropagation in HTML)
        if (fileRow && e.target.closest('button, a') === null) {
            const fileId = fileRow.dataset.fileId;
            const fileUrl = fileRow.dataset.fileUrl;
            const fileType = fileRow.dataset.fileType;
            const fileName = fileRow.dataset.filename;
            
            openPreviewModal(fileUrl, fileType, fileName);
        }
    });

    // --- Global Helpers ---
    window.deleteFile = async (fileId) => {
        const confirmed = await Modal.confirm('删除文件', '确定要删除此文件吗？');
        if (!confirmed) return;
        fetch(`/api/files/${fileId}`, { method: 'DELETE' })
            .then(async (res) => {
                let data = null;
                try { data = await res.json(); } catch (e) {}
                return { ok: res.ok, data };
            })
            .then(({ ok, data }) => {
                if (ok && data && data.status === 'ok') {
                    removeFileElement(fileId);
                    if (window.Toast) Toast.show('文件已删除');
                    updateBatchControls();
                } else {
                    const msg = data?.detail?.message || data?.message || '删除失败';
                    if (window.Toast) Toast.show(msg, 'error');
                }
            });
    };

    function removeFileElement(fileId) {
        const el = document.getElementById(`file-item-${fileId.replace(':', '-')}`);
        if (el) el.remove();
        
        // Check if empty
        const container = document.getElementById('file-list-disk');
        if (container && container.children.length === 0) {
            // Re-render empty state logic if needed, or let user refresh
            // Simple text fallback
            const isGridView = document.querySelector('.image-grid') !== null;
            if (isGridView) {
                 container.innerHTML = `
                    <div style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-tertiary);">
                        <p>暂无图片</p>
                    </div>`;
            } else {
                 container.innerHTML = `
                    <tr>
                        <td colspan="5" style="padding: 48px; text-align: center;">
                            <div class="text-muted">暂无文件</div>
                        </td>
                    </tr>`;
            }
        }
    }
});
