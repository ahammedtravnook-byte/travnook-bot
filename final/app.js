/**
 * Travnook Premium Dashboard - App Logic
 * Designed for stability, performance, and "awesome" UI feel.
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & State ---
    const STATE = {
        activeId: null,
        isDarkMode: false, // Default to light theme
        isHubOpen: false,
        activeHubTab: 'tab-behavior'
    };

    // --- DOM Elements ---
    const els = {
        chatList: document.getElementById('chat-list'),
        searchInput: document.getElementById('search-input'),
        emptyState: document.getElementById('empty-state'),
        chatView: document.getElementById('chat-view'),
        messagesContainer: document.getElementById('messages-container'),
        chatHeader: document.getElementById('chat-header'),
        chatInput: document.getElementById('chat-input'),
        activeTitle: document.getElementById('active-chat-title'),
        activeStatus: document.getElementById('active-chat-status'),
        themeToggle: document.getElementById('theme-toggle'),
        themeIcon: document.getElementById('theme-icon'),
        hubToggle: document.getElementById('hub-toggle'),
        hubView: document.getElementById('hub-view'),
        closeHub: document.getElementById('close-hub'),
        hubTabs: document.querySelectorAll('.hub-tab'),
        hubContents: document.querySelectorAll('.hub-content'),
        mobileBack: document.getElementById('mobile-back'),
        sidebar: document.getElementById('sidebar')
    };

    // --- Utility: Arabic Detection ---
    function isArabic(text) {
        const arabicRegex = /[\u0600-\u06FF]/;
        return arabicRegex.test(text);
    }

    // --- 1. Rendering Sidebar (606 Scenarios) ---
    function renderSidebar(query = '') {
        els.chatList.innerHTML = '';
        const searchStr = query.toLowerCase();

        const filtered = dashboardData.conversations.filter(convo => {
            if (convo.title.toLowerCase().includes(searchStr)) return true;
            return convo.messages.some(m => m.content.toLowerCase().includes(searchStr));
        });

        if (filtered.length === 0) {
            els.chatList.innerHTML = `
                <div class="flex flex-col items-center justify-center p-8 text-center opacity-40">
                    <i data-lucide="info" class="w-8 h-8 mb-2"></i>
                    <p class="text-sm">No matches found</p>
                </div>`;
            lucide.createIcons();
            return;
        }

        const fragment = document.createDocumentFragment();

        filtered.forEach(convo => {
            const lastMsg = convo.messages[convo.messages.length - 1];
            let preview = lastMsg ? lastMsg.content : "Empty scenario";
            if (preview.length > 35) preview = preview.substring(0, 35) + '...';

            const item = document.createElement('div');
            const isActive = STATE.activeId === convo.id;
            const hasArabic = isArabic(preview);
            
            item.className = `nav-card flex items-center gap-4 p-4 cursor-pointer rounded-2xl transition-all duration-200 
                ${isActive ? 'session-active bg-blue-500/10' : 'hover:bg-slate-100 dark:hover:bg-white/[0.03]'}`;
            
            item.innerHTML = `
                <div class="w-10 h-10 rounded-xl bg-slate-200 dark:bg-white/5 flex items-center justify-center shrink-0">
                    <span class="text-xs font-bold text-slate-500">${convo.id}</span>
                </div>
                <div class="flex-1 min-w-0 ${hasArabic ? 'text-right' : ''}" dir="${hasArabic ? 'rtl' : 'ltr'}">
                    <div class="flex justify-between items-center ${hasArabic ? 'flex-row-reverse' : ''}">
                        <h4 class="text-sm font-semibold truncate ${isActive ? 'text-blue-500' : ''}">${convo.title}</h4>
                        <span class="text-[10px] opacity-40">${convo.messages.length}</span>
                    </div>
                    <p class="text-xs opacity-50 truncate mt-0.5">${preview}</p>
                </div>
            `;

            item.onclick = () => selectSession(convo.id);
            fragment.appendChild(item);
        });

        els.chatList.appendChild(fragment);
        lucide.createIcons();
    }

    // --- 2. Session Selection ---
    function selectSession(id) {
        STATE.activeId = id;
        const convo = dashboardData.conversations.find(c => c.id === id);
        
        renderSidebar(els.searchInput.value);
        els.emptyState.classList.add('hidden');
        els.chatHeader.classList.remove('hidden');
        els.chatHeader.classList.add('flex');
        els.messagesContainer.classList.remove('hidden');
        els.chatInput.classList.remove('hidden');

        els.activeTitle.textContent = convo.title;
        
        const cmdMsg = convo.messages.find(m => m.content.startsWith('/'));
        els.activeStatus.innerHTML = cmdMsg 
            ? `<span class="cmd-pill">ACTIVE: ${cmdMsg.content}</span>` 
            : `SCENARIO FLOW • ${convo.messages.length} STEPS`;

        renderMessages(convo.messages);

        // Mobile: Show chat view
        if (window.innerWidth < 768) {
            document.body.classList.add('chat-open');
        }
    }

    // Mobile: Back Button Event
    els.mobileBack.onclick = () => {
        document.body.classList.remove('chat-open');
        STATE.activeId = null;
        renderSidebar(els.searchInput.value);
    };

    // --- 3. Message Rendering ---
    function renderMessages(messages) {
        els.messagesContainer.innerHTML = '';
        
        messages.forEach((msg, idx) => {
            const isBot = msg.role === 'assistant';
            const hasArabic = isArabic(msg.content);
            
            const wrapper = document.createElement('div');
            wrapper.className = `flex ${isBot ? 'justify-start' : 'justify-end'} animate-bubble`;
            wrapper.style.animationDelay = `${idx * 0.05}s`;

            const isCommand = msg.content.startsWith('/');
            
            let content = msg.content.replace(/\n/g, '<br>');
            if (isCommand) {
                content = `<span class="cmd-pill">${content}</span>`;
            }

            wrapper.innerHTML = `
                <div class="relative max-w-[85%] lg:max-w-[70%] p-4 lg:p-5 rounded-3xl shadow-sm text-[1.1rem] leading-relaxed bubble-shadow 
                    ${isBot 
                        ? 'bg-white dark:bg-[#1E1E22] text-slate-700 dark:text-slate-200 rounded-tl-none' 
                        : 'bg-blue-600 text-white rounded-tr-none'} 
                    ${hasArabic ? 'text-right' : 'text-left'}" 
                    dir="${hasArabic ? 'rtl' : 'ltr'}">
                    <div class="font-bold text-[10px] uppercase tracking-tighter opacity-40 mb-1 ${isBot ? 'text-blue-500' : 'text-white/70'}">
                        ${isBot ? 'Travnook Assistant' : 'Test Lead'}
                    </div>
                    <div class="break-words">${content}</div>
                </div>
            `;
            
            els.messagesContainer.appendChild(wrapper);
        });
        
        els.messagesContainer.scrollTo({
            top: els.messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }

    // --- 4. Hub Logic ---
    function initHub() {
        document.getElementById('tab-behavior').innerText = dashboardData.docs.behavior;
        document.getElementById('tab-goals').innerText = dashboardData.docs.goals;
        document.getElementById('tab-prompts').innerText = dashboardData.docs.prompts;

        els.hubToggle.onclick = () => {
            console.log("Opening Hub...");
            els.hubView.classList.add('hub-active');
            STATE.isHubOpen = true;
        };

        els.closeHub.onclick = () => {
            els.hubView.classList.remove('hub-active');
            STATE.isHubOpen = false;
        };

        els.hubTabs.forEach(tab => {
            tab.onclick = () => {
                const target = tab.dataset.target;
                els.hubTabs.forEach(t => {
                    t.classList.remove('active', 'text-blue-500', 'border-blue-500');
                    t.classList.add('text-slate-400');
                });
                tab.classList.add('active', 'text-blue-500', 'border-blue-500');
                tab.classList.remove('text-slate-400');

                els.hubContents.forEach(c => c.classList.add('hidden'));
                document.getElementById(target).classList.remove('hidden');
            };
        });
    }

    // --- 5. Theme & Search ---
    els.themeToggle.onclick = () => {
        document.documentElement.classList.toggle('dark');
        STATE.isDarkMode = !STATE.isDarkMode;
        els.themeIcon.setAttribute('data-lucide', STATE.isDarkMode ? 'sun' : 'moon');
        lucide.createIcons();
    };

    els.searchInput.oninput = (e) => {
        renderSidebar(e.target.value);
    };

    initHub();
    renderSidebar();
});
