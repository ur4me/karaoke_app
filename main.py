import http.server
import socketserver
import webbrowser
import threading
import urllib.request
import urllib.parse
import re
import json
import os

# 스크립트가 있는 폴더 기준으로 파일을 찾도록 수정 (실행 위치와 무관하게 동작)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================
# 🎨 프론트엔드 (HTML + CSS + JS) 
# ==========================================
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STEVE KARAOKE</title>
    <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #050505;
            --panel-bg: #111116;
            --neon-pink: #ff2a6d;
            --neon-cyan: #05d9e8;
            --text-main: #ffffff;
            --text-sub: #8c8c99;
            --border-color: #22222a;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Pretendard', sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); height: 100vh; overflow: hidden; }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--neon-cyan); }

        .app-container { display: flex; height: 100vh; width: 100%; }

        /* 왼쪽 패널 */
        .left-panel { flex: 1; min-width: 0; height: 100%; background-color: #000; position: relative; }
        #player { width: 100%; height: 100%; pointer-events: auto; z-index: 1; position: relative; }
        .player-placeholder {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            text-align: center; z-index: 0;
        }
        .mic-icon {
            font-size: 6rem; margin-bottom: 20px; color: var(--neon-pink);
            text-shadow: 0 0 20px rgba(255, 42, 109, 0.5);
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
            100% { transform: translateY(0px); }
        }

        /* 점수 화면 */
        .score-screen {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: black;
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 20;
        }
        .score-screen img {
            width: 100%; height: 100%;
            object-fit: cover;
            animation: fadeIn 0.5s ease-in-out;
        }
        /* 이미지 파일이 없을 때 대신 보여줄 화면 */
        .score-fallback {
            display: none;
            text-align: center;
            animation: fadeIn 0.5s ease-in-out;
        }
        .score-fallback .score-num {
            font-size: 10rem; font-weight: 900; font-style: italic;
            background: linear-gradient(90deg, #05d9e8 0%, #a67cff 50%, #ff2a6d 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-shadow: 0 0 40px rgba(255, 42, 109, 0.35);
        }
        .score-fallback .score-label {
            font-size: 1.6rem; font-weight: 800; color: var(--neon-cyan);
            letter-spacing: 4px; margin-top: 10px;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* 오른쪽 패널 */
        .right-panel {
            width: 400px; flex-shrink: 0; height: 100%; background-color: var(--panel-bg);
            border-left: 1px solid var(--border-color); display: flex; flex-direction: column;
            box-shadow: -5px 0 30px rgba(5, 217, 232, 0.05); overflow-x: hidden; position: relative;
        }

        /* 브랜드 헤더 */
        .brand-header { padding: 24px 20px; border-bottom: 1px solid var(--border-color); background-color: #0c0c10; }
        .logo-wrapper { display: flex; align-items: center; gap: 12px; }
        .mic-box {
            width: 44px; height: 44px; border: 2px solid var(--neon-cyan); flex-shrink: 0;
            border-radius: 12px; display: flex; align-items: center; justify-content: center;
            background-color: rgba(5, 217, 232, 0.05);
        }
        .mic-box svg { width: 22px; height: 22px; stroke: var(--neon-cyan); }
        .neon-title {
            font-size: 1.8rem; font-weight: 900; font-style: italic; text-transform: uppercase;
            background: linear-gradient(90deg, #05d9e8 0%, #a67cff 50%, #ff2a6d 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: 0.5px; margin-top: 2px;
        }

        /* 검색 영역 */
        .search-section { padding: 20px; z-index: 10; position: relative; }
        .search-section h2 { font-size: 1rem; color: var(--neon-pink); margin-bottom: 12px; font-weight: 800; letter-spacing: 1px; }
        .search-box { display: flex; gap: 8px; }
        .search-box input {
            flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border-color); min-width: 0;
            background-color: #1a1a24; color: var(--text-main); outline: none; transition: all 0.3s ease;
        }
        .search-box input:focus { border-color: var(--neon-cyan); box-shadow: 0 0 15px rgba(5, 217, 232, 0.3); }
        .search-box button {
            flex-shrink: 0; padding: 0 18px; border-radius: 8px; border: none; background-color: var(--neon-pink); color: white; 
            font-weight: 800; cursor: pointer; transition: all 0.3s ease; white-space: nowrap; box-shadow: 0 0 10px rgba(255, 42, 109, 0.4);
        }
        .search-box button:hover { background-color: #ff4d85; box-shadow: 0 0 20px rgba(255, 42, 109, 0.8); transform: translateY(-2px); }

        /* 검색 결과 */
        .search-results {
            position: absolute; top: 100%; left: 20px; right: 20px; margin-top: 5px;
            background-color: #1a1a24; border: 1px solid var(--neon-cyan);
            border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(5, 217, 232, 0.2);
            max-height: 400px; overflow-y: auto; display: none; z-index: 100;
        }
        .result-item { display: flex; gap: 12px; padding: 12px; border-bottom: 1px solid #2a2a35; cursor: pointer; transition: background-color 0.2s; }
        .result-item:hover { background-color: #252533; }
        .result-item img { width: 80px; height: 45px; border-radius: 4px; object-fit: cover; flex-shrink: 0; }
        .result-info { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
        .result-title { font-size: 0.85rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; line-height: 1.3;}

        /* 예약 목록 헤더 */
        .queue-header { 
            padding: 20px 20px 10px; font-size: 1rem; font-weight: 800; 
            display: flex; justify-content: space-between; align-items: center; color: var(--neon-cyan); letter-spacing: 1px;
        }
        .queue-count { 
            flex-shrink: 0; background: transparent; color: var(--neon-cyan); border: 1px solid var(--neon-cyan);
            padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; box-shadow: 0 0 5px rgba(5,217,232,0.3);
        }
        
        /* 스크롤 여백 수정 */
        .queue-section { flex: 1; overflow-y: auto; padding: 10px 20px 70px; overflow-x: hidden; }
        
        /* 큐 아이템 */
        .queue-item {
            display: flex; align-items: center; background-color: #16161e; padding: 12px; border-radius: 10px; 
            margin-bottom: 12px; gap: 12px; border: 1px solid #2a2a35; transition: all 0.2s; cursor: grab;
        }
        .queue-item:hover { transform: translateX(-5px); border-color: var(--neon-pink); box-shadow: 0 0 15px rgba(255, 42, 109, 0.2); }
        .queue-item:active { cursor: grabbing; }
        .queue-item.dragging { opacity: 0.5; border: 2px dashed var(--neon-cyan); background-color: #1a1a24; transform: scale(0.98); }
        .queue-item img { width: 64px; height: 48px; border-radius: 6px; object-fit: cover; pointer-events: none; flex-shrink: 0; }
        .queue-info { flex: 1; min-width: 0; overflow: hidden; pointer-events: none; }
        .queue-title { font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; font-weight: 600;}
        .queue-status { font-size: 0.75rem; color: var(--neon-cyan); display: flex; align-items: center; gap: 4px; }
        .drag-handle { font-size: 1rem; color: var(--text-sub); }
        .delete-btn { 
            flex-shrink: 0; background: transparent; border: 1px solid #555; color: #aaa; 
            padding: 6px 10px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; transition: all 0.2s; 
        }
        .delete-btn:hover { border-color: var(--neon-pink); color: var(--neon-pink); }
        .empty-queue { text-align: center; color: var(--text-sub); margin-top: 40px; font-size: 0.9rem; }

        /* 하단 컨트롤 영역 */
        .bottom-controls {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            z-index: 50;
        }
        .control-btn {
            background-color: rgba(26, 26, 36, 0.85);
            backdrop-filter: blur(5px);
            padding: 8px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 800;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        .skip-btn {
            color: var(--neon-pink);
            border: 1px solid var(--neon-pink);
        }
        .skip-btn:hover {
            background-color: var(--neon-pink);
            color: #fff;
            box-shadow: 0 0 15px rgba(255, 42, 109, 0.6);
        }
        .fullscreen-btn {
            color: var(--neon-cyan);
            border: 1px solid var(--neon-cyan);
        }
        .fullscreen-btn:hover {
            background-color: var(--neon-cyan);
            color: #000;
            box-shadow: 0 0 15px rgba(5, 217, 232, 0.6);
        }
    </style>
</head>
<body>
    <audio id="fanfareAudio" src="/fanfare.mp3" preload="auto"></audio>

    <div class="app-container">
        <!-- 왼쪽 패널 -->
        <div class="left-panel">
            <div id="placeholder" class="player-placeholder">
                <div class="mic-icon">🎤</div>
                <h2 style="color: white; font-weight: 800; font-size: 1.5rem; margin-bottom:10px;">리모컨으로 곡을 예약해주세요</h2>
                <p style="color: var(--neon-cyan);">우측 검색창에 가수나 제목을 입력하세요</p>
            </div>
            
            <!-- 점수 화면 -->
            <div id="scoreScreen" class="score-screen">
                <img id="scoreImg" src="/image_d05c44.jpg" alt="100점 축하 화면">
                <div id="scoreFallback" class="score-fallback">
                    <div class="score-num">100</div>
                    <div class="score-label">PERFECT SCORE! 🎉</div>
                </div>
            </div>

            <div id="player"></div>
        </div>

        <!-- 오른쪽 패널 -->
        <div class="right-panel">
            <div class="brand-header">
                <div class="logo-wrapper">
                    <div class="mic-box">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="22"></line>
                        </svg>
                    </div>
                    <div class="neon-title">STEVE KARAOKE</div>
                </div>
            </div>

            <div class="search-section">
                <h2>🎵 SEARCH & RESERVE</h2>
                <div class="search-container">
                    <div class="search-box">
                        <input type="text" id="searchInput" placeholder="예: 아이유 밤편지" autocomplete="off" />
                        <button id="searchBtn">검색</button>
                    </div>
                    <div id="searchResults" class="search-results"></div>
                </div>
            </div>
            
            <div class="queue-header">
                <span>▶ PLAYLIST</span>
                <span class="queue-count" id="queueCount">0</span>
            </div>
            <div class="queue-section" id="queueList">
                <div class="empty-queue">대기 중인 곡이 없습니다.</div>
            </div>

            <!-- 하단 컨트롤 버튼 모음 -->
            <div class="bottom-controls">
                <button id="skipBtn" class="control-btn skip-btn">⏭ 다음 곡</button>
                <button id="fullscreenBtn" class="control-btn fullscreen-btn">⛶ 전체화면</button>
            </div>
        </div>
    </div>

    <script>
        let player;
        let queue = [];
        let isPlayerIdle = true;
        let isShowingScore = false;   // 점수 화면 표시 중 플래그 (중복 재생/스킵 방지)
        
        const fanfareAudio = document.getElementById('fanfareAudio');

        // [수정] 이미지 미리 로드 → 점수 화면이 뜨는 순간 바로 보이도록
        const preloadImg = new Image();
        preloadImg.src = '/image_d05c44.jpg';

        // [수정] 이미지 파일이 없으면(404) 대체 화면 표시
        document.getElementById('scoreImg').addEventListener('error', function() {
            this.style.display = 'none';
            document.getElementById('scoreFallback').style.display = 'block';
        });

        // [수정] 진짜 오디오 잠금 해제: load()가 아니라 muted 상태로 play→pause를 해야
        // 브라우저 자동재생 정책이 풀림
        document.body.addEventListener('click', function unlockAudio() {
            fanfareAudio.muted = true;
            const p = fanfareAudio.play();
            if (p !== undefined) {
                p.then(() => {
                    fanfareAudio.pause();
                    fanfareAudio.currentTime = 0;
                    fanfareAudio.muted = false;
                }).catch(() => { fanfareAudio.muted = false; });
            }
            document.body.removeEventListener('click', unlockAudio);
        }, { once: true });

        const tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        function onYouTubeIframeAPIReady() {
            player = new YT.Player('player', {
                height: '100%', width: '100%', videoId: '',
                // [수정] fs:0 → 유튜브 자체 전체화면 버튼 비활성화.
                // 유튜브 자체 전체화면을 쓰면 iframe이 화면 전체를 덮어서
                // 점수 화면이 절대 보이지 않음. 대신 앱의 ⛶ 전체화면 버튼 사용.
                playerVars: { 'autoplay': 1, 'controls': 1, 'fs': 0, 'rel': 0 },
                events: { 'onStateChange': onPlayerStateChange }
            });
        }

        function onPlayerStateChange(event) {
            if (event.data === YT.PlayerState.ENDED) {
                // [수정] stopVideo() 호출로도 ENDED가 발생할 수 있으므로,
                // 이미 점수 화면 중이거나 대기 상태면 무시 (중복 방지)
                if (isShowingScore || isPlayerIdle) return;
                isPlayerIdle = true;
                showScoreScreen();
            } else if (event.data === YT.PlayerState.PLAYING) {
                isPlayerIdle = false; 
                document.getElementById('placeholder').style.display = 'none';
            }
        }

        function showScoreScreen() {
            isShowingScore = true;
            const scoreScreen = document.getElementById('scoreScreen');
            scoreScreen.style.display = 'flex';
            
            fanfareAudio.currentTime = 0;
            const playPromise = fanfareAudio.play();
            if (playPromise !== undefined) {
                playPromise.catch(e => console.log("팡파르 자동 재생 차단됨:", e));
            }

            setTimeout(() => {
                scoreScreen.style.display = 'none';
                fanfareAudio.pause();
                fanfareAudio.currentTime = 0;
                isShowingScore = false;
                playNextSong();
            }, 3000);
        }

        async function performSearch() {
            const input = document.getElementById('searchInput');
            let query = input.value.trim();
            if(!query) return;
            if(!query.includes('노래방') && !query.includes('karaoke')) query += ' 노래방';

            const btn = document.getElementById('searchBtn');
            const resultsBox = document.getElementById('searchResults');
            btn.innerText = '검색중'; btn.disabled = true;
            resultsBox.innerHTML = '<div style="padding: 15px; text-align:center; color:#05d9e8;">검색 중... ⏳</div>';
            resultsBox.style.display = 'block';

            try {
                const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                if(data.length === 0) resultsBox.innerHTML = '<div style="padding: 15px; text-align:center; color:#8c8c99;">검색 결과가 없습니다.</div>';
                else renderSearchResults(data);
            } catch(e) {
                resultsBox.innerHTML = '<div style="padding: 15px; text-align:center; color:#ff2a6d;">오류가 발생했습니다.</div>';
            } finally {
                btn.innerText = '검색'; btn.disabled = false;
            }
        }

        function renderSearchResults(results) {
            const resultsBox = document.getElementById('searchResults');
            resultsBox.innerHTML = '';
            results.forEach(video => {
                const item = document.createElement('div');
                item.className = 'result-item';
                const thumbUrl = `https://img.youtube.com/vi/${video.id}/mqdefault.jpg`;
                item.innerHTML = `
                    <img src="${thumbUrl}" alt="thumbnail">
                    <div class="result-info">
                        <div class="result-title" title="${video.title}">${video.title}</div>
                    </div>
                `;
                item.addEventListener('click', () => {
                    reserveSong(video.id, video.title, thumbUrl);
                    resultsBox.style.display = 'none';
                    document.getElementById('searchInput').value = '';
                });
                resultsBox.appendChild(item);
            });
        }

        function reserveSong(id, title, thumbUrl) {
            queue.push({ id, title, thumb: thumbUrl });
            renderQueue();
            // [수정] 점수 화면이 나오는 3초 동안 예약하면 곡이 겹쳐 재생되던 버그 방지
            if (isPlayerIdle && !isShowingScore) playNextSong();
        }

        function playNextSong() {
            if (queue.length > 0) {
                const nextSong = queue.shift();
                isPlayerIdle = false;
                player.loadVideoById(nextSong.id);
                renderQueue();
            } else {
                isPlayerIdle = true;
                document.getElementById('placeholder').style.display = 'block';
                player.stopVideo(); 
            }
        }

        function removeFromQueue(index) {
            queue.splice(index, 1);
            renderQueue();
        }

        function renderQueue() {
            const list = document.getElementById('queueList');
            document.getElementById('queueCount').innerText = queue.length;
            list.innerHTML = '';
            if (queue.length === 0) {
                list.innerHTML = `<div class="empty-queue">대기 중인 곡이 없습니다.</div>`; return;
            }
            queue.forEach((song, index) => {
                const item = document.createElement('div'); 
                item.className = 'queue-item';
                item.draggable = true;
                item.dataset.index = index;
                item.addEventListener('dragstart', () => item.classList.add('dragging'));
                item.addEventListener('dragend', () => item.classList.remove('dragging'));
                item.innerHTML = `
                    <img src="${song.thumb}" alt="thumbnail">
                    <div class="queue-info">
                        <div class="queue-title" title="${song.title}">${song.title}</div>
                        <div class="queue-status">대기 번호 ${index + 1}번 <span class="drag-handle">≡</span></div>
                    </div>
                    <button class="delete-btn" onclick="removeFromQueue(${index})">취소</button>
                `;
                list.appendChild(item);
            });
        }

        const queueListContainer = document.getElementById('queueList');
        queueListContainer.addEventListener('dragover', e => {
            e.preventDefault();
            const afterElement = getDragAfterElement(queueListContainer, e.clientY);
            const draggable = document.querySelector('.dragging');
            if (draggable) {
                if (afterElement == null) queueListContainer.appendChild(draggable);
                else queueListContainer.insertBefore(draggable, afterElement);
            }
        });
        queueListContainer.addEventListener('drop', e => {
            e.preventDefault();
            const currentDOMItems = [...queueListContainer.querySelectorAll('.queue-item')];
            const newQueue = currentDOMItems.map(item => {
                const originalIndex = parseInt(item.dataset.index);
                return queue[originalIndex];
            });
            queue = newQueue;
            renderQueue(); 
        });

        function getDragAfterElement(container, y) {
            const draggableElements = [...container.querySelectorAll('.queue-item:not(.dragging)')];
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect();
                const offset = y - box.top - box.height / 2;
                if (offset < 0 && offset > closest.offset) return { offset: offset, element: child };
                else return closest;
            }, { offset: Number.NEGATIVE_INFINITY }).element;
        }

        document.getElementById('searchBtn').addEventListener('click', performSearch);
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') performSearch();
        });
        document.addEventListener('click', function(e) {
            const searchContainer = document.querySelector('.search-container');
            if(!searchContainer.contains(e.target)) document.getElementById('searchResults').style.display = 'none';
        });

        document.getElementById('skipBtn').addEventListener('click', () => {
            // [수정] 기존에는 stopVideo() 후 playNextSong()을 불렀는데,
            // stopVideo()가 ENDED 이벤트를 추가로 발생시켜 곡이 두 개씩 건너뛰거나
            // 점수 화면이 꼬이는 원인이 됨. loadVideoById가 알아서 교체하므로
            // stopVideo 없이 바로 다음 곡으로 넘어감.
            if (!isPlayerIdle && !isShowingScore) {
                playNextSong(); 
            }
        });

        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log(`전체화면 오류: ${err.message}`);
                });
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });
    </script>
</body>
</html>
"""

# ==========================================
# 🚀 파이썬 백엔드 서버
# ==========================================
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def serve_static(self, filename, content_type):
        """스크립트 폴더 기준으로 정적 파일 서빙 + 없으면 경고 출력"""
        filepath = os.path.join(BASE_DIR, filename)
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            print(f"⚠️  경고: '{filename}' 파일을 찾을 수 없습니다. 이 위치에 넣어주세요 → {filepath}")
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
            
        elif self.path == '/image_d05c44.jpg':
            self.serve_static('image_d05c44.jpg', 'image/jpeg')

        elif self.path == '/fanfare.mp3':
            self.serve_static('fanfare.mp3', 'audio/mpeg')
                
        elif self.path.startswith('/search?q='):
            query = urllib.parse.unquote(self.path.split('q=')[1])
            results = self.search_youtube(query)
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(results).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def search_youtube(self, query):
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8')
            results = []
            pattern = r'"videoRenderer":\{"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}\]'
            for match in re.finditer(pattern, html):
                vid = match.group(1)
                raw_title = match.group(2) 
                try: title = json.loads(f'"{raw_title}"')
                except: title = raw_title 
                if not any(r['id'] == vid for r in results):
                    results.append({"id": vid, "title": title})
                if len(results) >= 10: break
            return results
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            return []

def run_server():
    # Render는 PORT 환경변수로 포트를 지정해줌. 로컬에서는 8080 사용.
    port = int(os.environ.get("PORT", 8080))
    is_render = os.environ.get("RENDER") is not None

    # 시작 시 필수 파일 존재 여부 미리 점검
    for fname in ['image_d05c44.jpg', 'fanfare.mp3']:
        if not os.path.exists(os.path.join(BASE_DIR, fname)):
            print(f"⚠️  '{fname}' 파일이 없습니다! 이 파일을 다음 폴더에 넣어주세요: {BASE_DIR}")

    # ThreadingTCPServer: 요청을 스레드로 처리해서 여러 접속/느린 요청에도 안 멈춤
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", port), RequestHandler) as httpd:
        print(f"\n🎤 STEVE KARAOKE 서버가 시작되었습니다! (Render 배포 대응 버전)")
        print(f"👉 접속 주소: http://localhost:{port}\n")
        # 로컬 실행일 때만 브라우저 자동 열기 (서버 환경에서는 의미 없음)
        if not is_render:
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()